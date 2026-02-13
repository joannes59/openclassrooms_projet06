from pathlib import Path
import mlflow
import json

import logging

def main():


    #logging.getLogger("mlflow").setLevel(logging.ERROR)
    
    
    
    # configuration des parametres de connection et des repertoires de travail
    MLFLOW_URL = "http://localhost:5000"
    DATA_DIR = str(Path.home() / "data")
    EXPERIMENT_NAME = "Projet 06 - OpenClassrooms"
    
    # répertoire de l'entrée mlflow
    cwd = Path.cwd()
    init_mlflow_dir = str(cwd.resolve()) + "/src/mlflow"
    print('Répertoire de l entrée MLproject:\n', init_mlflow_dir)
    
    
    config_mlflow = mlflow.run(
                            uri=init_mlflow_dir,
                            entry_point="check",
                            parameters={
                                "mlflow_url": MLFLOW_URL,
                                "data_dir": DATA_DIR,
                                "experiment_name": EXPERIMENT_NAME
                                },
                            )
    
    print('résultat de la fonction check mlflow', config_mlflow.get_status(), config_mlflow.run_id, config_mlflow)


if __name__ == "__main__":
    main()
