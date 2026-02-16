#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 2026
Version 2 - Vérification du serveur MLflow via MLflowClient

@author: joannes
"""

import argparse
import sys
import tempfile
import logging
from pathlib import Path
import json
from mlflow import MlflowClient

MLFLOW_URL = "http://localhost:5000"
DATA_DIR = str(Path.home() / "data")
EXPERIMENT_NAME = "Projet 06 - OpenClassrooms"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check MLflow server and data directory (v2)"
    )

    parser.add_argument(
        "--mlflow_url",
        type=str,
        default=MLFLOW_URL,
        help="URL du serveur MLflow (défaut: http://localhost:5000)",
    )

    parser.add_argument(
        "--data_dir",
        type=str,
        default=DATA_DIR,
        help="Répertoire des données (défaut: $HOME/data)",
    )

    parser.add_argument(
        "--experiment_name",
        type=str,
        default=EXPERIMENT_NAME,
        help="Nom de l'expérimentation (défaut: Projet 06 - OpenClassrooms)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Activer les logs détaillés",
    )

    return parser.parse_args()


def check_mlflow(client: MlflowClient) -> bool:
    """Vérifie si le serveur MLflow est accessible."""
    try:
        client.get_experiment_by_name("test")
        logging.info("MLflow est en ligne")
        return True
    except Exception as e:
        logging.error(f"MLflow inaccessible: {e}")
        return False


def get_or_create_experiment(client: MlflowClient, experiment_name: str) -> str:
    """Récupère ou crée une expérience et retourne l'experiment_id."""
    exp = client.get_experiment_by_name(experiment_name)

    if exp:
        logging.info(f"Expérience trouvée: {exp.experiment_id}")
        return exp.experiment_id

    exp_id = client.create_experiment(experiment_name)
    logging.info(f"Expérience créée: {exp_id}")
    return exp_id


def check_data_directory(data_dir: Path) -> dict:
    """Vérifie le répertoire de données et retourne les infos."""
    raw_files = []
    processed_files = []

    if not data_dir.exists():
        logging.warning("Le dossier data n'existe pas.")
        return {"exists": False, "raw_files": [], "processed_files": []}

    logging.info("Dossier data trouvé")

    raw_dir = data_dir / "raw"
    if raw_dir.exists():
        raw_files = [f.name for f in raw_dir.glob("*.csv")]

    processed_dir = data_dir / "processed"
    if processed_dir.exists():
        processed_files = [f.name for f in processed_dir.glob("*.csv")]

    return {
        "exists": True,
        "raw_files": raw_files,
        "raw_count": len(raw_files),
        "processed_files": processed_files,
        "processed_count": len(processed_files),
    }


def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    mlflow_url = args.mlflow_url.rstrip("/")
    data_dir = Path(args.data_dir).expanduser().resolve()
    experiment_name = args.experiment_name

    logging.info(f"MLFLOW_URL: {mlflow_url}")
    logging.info(f"DATA_DIR: {data_dir}")
    logging.info(f"EXPERIMENT_NAME: {experiment_name}")

    client = MlflowClient(tracking_uri=mlflow_url)

    if not check_mlflow(client):
        sys.exit(1)

    data_info = check_data_directory(data_dir)

    exp_id = get_or_create_experiment(client, experiment_name)

    run = client.create_run(exp_id)
    run_id = run.info.run_id
    logging.info(f"Run créé: {run_id}")

    client.log_param(run_id, "mlflow_url", mlflow_url)
    client.log_param(run_id, "data_dir", str(data_dir))
    client.log_param(run_id, "experiment_name", experiment_name)
    client.log_param(run_id, "data_exists", str(data_info["exists"]))

    if data_info["exists"]:
        client.log_metric(run_id, "raw_files_count", data_info["raw_count"])
        client.log_metric(run_id, "processed_files_count", data_info["processed_count"])

        if data_info["raw_files"]:
            artifact_content = json.dumps(
                {
                    "raw_files": data_info["raw_files"],
                    "processed_files": data_info["processed_files"],
                },
                indent=2,
            )

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                f.write(artifact_content)
                client.log_artifact(run_id, f.name, artifact_path="data_files")
                
            client.log_text(run_id, artifact_content, "data_files/config.json")
            #Path(f.name).unlink()

    client.set_terminated(run_id, status="FINISHED")
    logging.info(f"Run terminé: {run_id}")

    result = {
        "mlflow_url": mlflow_url,
        "data_dir": str(data_dir),
        "experiment_name": experiment_name,
        "run_id": run_id,
        "data_info": data_info,
    }

    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    main()
