#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 17:35:07 2026

@author: joannes
"""

import argparse
import sys
import requests
import logging
from pathlib import Path
import json

MLFLOW_URL = "http://localhost:5000"
DATA_DIR = str(Path.home() / "data")
EXPERIMENT_NAME = "Projet 06 - OpenClassrooms"


def get_or_create_experiment(mlflow_url: str, experiment_name: str) -> str:
    """Récupère ou crée une expérience et retourne l'experiment_id."""
    # Cherche l'expérience par nom
    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/experiments/search",
        json={"filter": f"name = '{experiment_name}'", "max_results": 1},
    )

    if resp.status_code == 200:
        experiments = resp.json().get("experiments", [])
        if experiments:
            return experiments[0].get("experiment_id")

    # Crée l'expérience si elle n'existe pas
    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/experiments/create",
        json={"name": experiment_name},
    )

    if resp.status_code == 200:
        return resp.json().get("experiment", {}).get("experiment_id")

    # Si erreur, afficher le message
    print(f"Error: {resp.status_code} - {resp.text}")
    raise Exception(f"Cannot find or create experiment: {experiment_name}")


def create_run(mlflow_url: str, experiment_name: str) -> str:
    """Crée un run via l'API REST et retourne le run_id."""
    exp_id = get_or_create_experiment(mlflow_url, experiment_name)
    print(f"Using experiment_id: {exp_id}")

    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/runs/create", json={"experiment_id": exp_id}
    )

    # Debug: afficher la réponse
    print(f"Create run response status: {resp.status_code}")
    print(f"Create run response body: {resp.json()}")

    run_id = resp.json().get("run", {}).get("info", {}).get("run_id")
    if not run_id:
        raise Exception(f"Failed to get run_id from response: {resp.json()}")
    return run_id


def log_param(mlflow_url: str, run_id: str, key: str, value: str):
    """Log un paramètre via l'API REST."""
    print(f"Logging param: {key}={value} for run_id: {run_id}")
    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/runs/log-parameter",
        json={"run_id": run_id, "key": key, "value": str(value)},
    )
    print(f"Log param response: {resp.status_code} - {resp.text}")
    if resp.status_code != 200:
        print(f"Error logging param {key}: {resp.status_code} - {resp.text}")


def log_metric(mlflow_url: str, run_id: str, key: str, value: float):
    """Log une métrique via l'API REST."""
    print(f"Logging metric: {key}={value} for run_id: {run_id}")
    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/runs/log-metric",
        json={"run_id": run_id, "metric": {"key": key, "value": value, "step": 0}},
    )
    print(f"Log metric response: {resp.status_code} - {resp.text}")
    if resp.status_code != 200:
        print(f"Error logging metric {key}: {resp.status_code} - {resp.text}")


def end_run(mlflow_url: str, run_id: str, status: str = "FINISHED"):
    """Termine un run via l'API REST."""
    resp = requests.post(
        f"{mlflow_url}/api/2.0/mlflow/runs/update",
        json={"run_id": run_id, "status": status},
    )
    if resp.status_code != 200:
        print(f"Error ending run: {resp.status_code} - {resp.text}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check MLflow server and data directory"
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

    return parser.parse_args()


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def check_mlflow(url: str) -> bool:
    try:
        logging.debug(f"Vérification de {url}/health")
        response = requests.get(f"{url}/health", timeout=3)

        if response.status_code == 200:
            logging.info("MLflow est en ligne ✅")
            return True
        else:
            logging.error(f"MLflow répond mais code inattendu: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        logging.error(f"MLflow inaccessible ❌ : {e}")
        return False


def main():
    args = parse_args()

    mlflow_url = args.mlflow_url.rstrip("/")
    data_dir = Path(args.data_dir).expanduser().resolve()
    experiment_name = args.experiment_name
    raw_files = []

    logging.info(f"MLFLOW_URL : {mlflow_url}")
    logging.info(f"DATA_DIR   : {data_dir}")
    logging.info(f"EXPERIMENT_NAME   : {experiment_name}")

    if not check_mlflow(mlflow_url):
        sys.exit(1)

    if not data_dir.exists():
        logging.warning("Le dossier data n'existe pas.")
    else:
        logging.info("Dossier data trouvé ✅")
        raw_dir = data_dir / "raw"
        raw_files = [f.name for f in raw_dir.glob("*.csv")]

    # Log via REST API
    run_id = create_run(mlflow_url, experiment_name)
    print("--------run_id----------", run_id)
    log_param(mlflow_url, run_id, "mlflow_url", mlflow_url)
    log_param(mlflow_url, run_id, "data_dir", str(data_dir))
    log_param(mlflow_url, run_id, "experiment_name", experiment_name)
    log_param(mlflow_url, run_id, "data_exists", str(data_dir.exists()))

    if raw_files:
        log_metric(mlflow_url, run_id, "raw_files_count", len(raw_files))

    end_run(mlflow_url, run_id, "FINISHED")

    # Retourne les infos
    result = {
        "mlflow_url": mlflow_url,
        "data_dir": str(data_dir),
        "experiment_name": experiment_name,
        "raw_files": raw_files,
        "raw_files_count": len(raw_files),
        "run_id": run_id,
    }

    return result


if __name__ == "__main__":
    main()
