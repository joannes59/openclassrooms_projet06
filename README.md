# 🚀 ML Lifecycle Management : Scoring de Crédit avec MLflow

[![MLflow](https://img.shields.io/badge/MLflow-Tracking-blueviolet?style=flat-square&logo=mlflow)](https://mlflow.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Latest-orange?style=flat-square&logo=scikit-learn)](https://scikit-learn.org/)

## 📌 Présentation du Projet
Ce projet est réalisé dans le cadre du parcours **MLOps d'OpenClassrooms**. Il porte sur la mise en œuvre d'une solution de **classification binaire** pour le scoring de crédit, avec un focus majeur sur la gestion du cycle de vie du modèle.

L'objectif est d'industrialiser la démarche de Data Science en utilisant **MLflow** pour assurer la traçabilité complète des expérimentations, de l'analyse exploratoire jusqu'au packaging du modèle final.

## 🎯 Problématique Métier
L'enjeu consiste à prédire la probabilité de défaut de paiement d'un client. Dans ce cadre, la rigueur du suivi est cruciale pour :
* **Comparer objectivement** différentes architectures (Random Forest, XGBoost, etc.).
* **Optimiser les hyperparamètres** de manière systématique.
* **Justifier les seuils de décision** en fonction de l'impact métier (arbitrage entre risque de crédit et opportunité commerciale).

## 🛠️ Compétences MLOps Démontrées
* **Tracking d'expériences :** Centralisation des paramètres, métriques (AUC, Recall, Precision) et versions de modèles via MLflow.
* **Standardisation :** Packaging des modèles au format standard pour simplifier le déploiement futur.
* **Rigueur Scientifique :** Documentation systématique de chaque essai pour garantir la reproductibilité des résultats.
* **Optimisation :** Recherche fine des meilleures configurations d'hyperparamètres.

---

## ⚙️ Installation

### Prérequis

1. **UV (gestionnaire de paquets Python)**
   - Documentation officielle : https://docs.astral.sh/uv/
   - Installation rapide :
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Miniconda (alternative pour projets MLflow)**
   - Documentation : https://docs.conda.io/en/latest/miniconda.html
   - Recommandé pour les environnements MLflow complexes

### Configuration du projet

Les dépendances sont définies dans `pyproject.toml`. Le projet utilise automatiquement UV pour gérer l'environnement virtuel.

---

## 🚀 Utilisation

### Démarrage des serveurs

#### Serveur MLflow
Lance le serveur de tracking MLflow pour suivre vos expérimentations :
```bash
./start_mlflow.sh
```
Le serveur sera accessible sur http://localhost:5000

#### Jupyter Notebook
Démarre Jupyter Notebook pour l'analyse exploratoire :
```bash
./start_jupyter.sh
```
Les notebooks sont accessible sur http://localhost:8888

> **Note de sécurité :** Ce projet étant un démonstrateur, les connexions aux serveurs MLflow et Jupyter ne disposent d'aucune authentification ni sécurité renforcée. Ne l'utilisez pas en environnement de production.

---

## 🏗️ Structure du Projet

### Structure des données
Par défaut, les données sont stockées dans le répertoire utilisateur :
```text
~/data/               # Données du projet
├── raw/             # Données brutes non traitées
├── processed/       # Données nettoyées et prêtes pour le pipeline
└── describe_column.csv  # Description des colonnes des dataframes
```

### Structure du code source
```text
├── main.py                     # Point d'entrée principal de l'application
├── notebooks/                  # EDA (Analyse Exploratoire) et prototypage
│   ├── Initiez-vous au MLOps 1-01 MLflow.ipynb
│   ├── Initiez-vous au MLOps 1-02 exploration.ipynb
│   └── Initiez-vous au MLOps 1-03 training.ipynb
├── src/                        # Code source
│   ├── data/                   # Scripts de traitement des données
│   │   ├── preprocess.py       # Prétraitement des données
│   │   └── exploration.py      # Analyse exploratoire et description des colonnes
│   └── mlflow/                 # Scripts et configuration MLflow
│       ├── check_mlflow.py     # Vérification du serveur MLflow via API REST
│       ├── MLproject           # Configuration MLproject pour mlflow run
│       └── conda.yaml           # Environnement Conda pour les runs MLflow
├── start_mlflow.sh             # Script de démarrage du serveur MLflow
├── start_jupyter.sh            # Script de démarrage de Jupyter Notebook
├── pyproject.toml              # Configuration des dépendances et du projet
├── uv.lock                     # Fichier de verrouillage des dépendances UV
├── requirement.txt             # Dépendances Python (alternative)
├── .python-version             # Version Python utilisée
├── .gitignore                  # Fichiers ignorés par Git
├── LICENSE                     # Licence du projet
└── README.md                   # Documentation du projet
```

> **Configuration des chemins :** Les chemins vers les données peuvent être personnalisés lors du lancement du serveur MLflow en utilisant l'argument `--data-path` :
> ```bash
> ./start_mlflow.sh /chemin/vers/vos/données
> ```