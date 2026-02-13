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
import mlflow
import json

MLFLOW_URL = "http://localhost:5000"
DATA_DIR = str(Path.home() / "data")
EXPERIMENT_NAME = "Projet 06 - OpenClassrooms"


def parse_args():
    parser = argparse.ArgumentParser(description="Check MLflow server and data directory")

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
        

    # Configure MLflow côté client
    mlflow.set_tracking_uri(mlflow_url)
    mlflow.set_experiment(experiment_name)

    # Retourne les infos 
    result = {
        "mlflow_url": mlflow_url,
        "data_dir": str(data_dir),
        "experiment_name": experiment_name,
        "raw_files": raw_files
        }



    # Affiche le JSON
    json_output = json.dumps(result, indent=4)

    return json_output


if __name__ == "__main__":
    main()
