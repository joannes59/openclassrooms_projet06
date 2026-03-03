import sys
import pandas as pd
from pathlib import Path
import argparse

# Colonnes pertinentes pour le modèle de scoring
SELECTED_COLUMNS = ['TARGET', 'EXT_SOURCE_3', 'EXT_SOURCE_2', 'EXT_SOURCE_1', 'DAYS_BIRTH', 'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 
                    'DAYS_LAST_PHONE_CHANGE', 'CODE_GENDER', 'DAYS_ID_PUBLISH', 'REG_CITY_NOT_WORK_CITY',  'REGION_RATING_CLIENT_W_CITY', 
                    'REGION_RATING_CLIENT', 'FLAG_EMP_PHONE', 'ORGANIZATION_TYPE', 'DAYS_EMPLOYED', 'REG_CITY_NOT_LIVE_CITY', 'FLAG_DOCUMENT_3', 
                    'FLOORSMAX_AVG', 'FLOORSMAX_MEDI', 'FLOORSMAX_MODE', 'OCCUPATION_TYPE']


def select_columns(df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
    """
    Sélectionne les colonnes pertinentes pour le modèle

    Args:
        df: DataFrame d'entrée
        columns: Liste des colonnes à garder (défaut: SELECTED_COLUMNS)

    Returns:
        DataFrame avec uniquement les colonnes sélectionnées
    """
    if columns is None:
        columns = SELECTED_COLUMNS

    # Vérifie que les colonnes existent
    available_cols = [col for col in columns if col in df.columns]
    missing_cols = [col for col in columns if col not in df.columns]

    if missing_cols:
        print(f"Colonnes manquantes: {missing_cols}")

    print(f"Sélection de {len(available_cols)} colonnes: {available_cols}")

    return df[available_cols]


def load_application_train(data_dir=None):
    """
    Charge les données principales depuis application_train.csv

    Args:
        data_dir: Répertoire des données (défaut: ~/data)

    Returns:
        DataFrame avec les données brutes
    """
    if data_dir is None:
        data_dir = Path.home() / "data"
    else:
        data_dir = Path(data_dir)

    print(f"data_dir: {data_dir}")
    raw_dir = data_dir / "raw"

    file_path = raw_dir / "application_train.csv"
    print(f"Chargement de {file_path}...")

    df = pd.read_csv(file_path)

    print(f"Shape: {df.shape}")
    print(f"Mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    return df


def handle_missing_values(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """
    Gère les valeurs manquantes

    Args:
        df: DataFrame d'entrée
        threshold: Seuil de suppression des colonnes (>50% manquant par défaut)

    Returns:
        DataFrame nettoyé
    """
    df = df.copy()

    # Supprime les colonnes avec trop de valeurs manquantes
    missing_ratio = df.isnull().sum() / len(df)
    cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()

    if cols_to_drop:
        print(
            f"Suppression des colonnes (> {threshold * 100}% manquant): {len(cols_to_drop)}"
        )
        df = df.drop(columns=cols_to_drop)

    # Remplissage des valeurs numériques par la médiane
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    for col in numeric_cols:
        if df[col].isnull().sum() > 0:
            df.loc[:, col] = df[col].fillna(df[col].median())

    # Remplissage des valeurs catégorielles par le mode
    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        if df[col].isnull().sum() > 0:
            df.loc[:, col] = df[col].fillna(df[col].mode().iloc[0])

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Supprime les doublons
    """
    df = df.copy()

    n_before = len(df)
    df = df.drop_duplicates()
    n_after = len(df)

    if n_before != n_after:
        print(f"Doublons supprimés: {n_before - n_after}")

    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline complet de preprocessing
    """
    df = remove_duplicates(df)
    #df = handle_missing_values(df)
    return df


def save_processed_data(
    df: pd.DataFrame,
    filename: str = "application_train_processed.parquet",
    data_dir=None,
) -> str:
    """
    Sauvegarde le DataFrame traité au format parquet

    Args:
        df: DataFrame à sauvegarder
        filename: Nom du fichier (défaut: application_train_processed.parquet)
        data_dir: Répertoire des données (défaut: ~/data)

    Returns:
        Chemin du fichier sauvegardé
    """
    if data_dir is None:
        data_dir = Path.home() / "data"
    else:
        data_dir = Path(data_dir)

    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    file_path = processed_dir / filename
    df.to_parquet(file_path, index=False)

    print(f"DataFrame sauvegardé: {file_path}")
    print(f"Shape: {df.shape}")
    print(f"Mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    return str(file_path)


def main():
    

    parser = argparse.ArgumentParser(description="Preprocessing pipeline")
    parser.add_argument(
        "--data_dir", type=str, default="~/data", help="Répertoire des données"
    )
    parser.add_argument(
        "--output_filename",
        type=str,
        default="application_train_processed.parquet",
        help="Nom du fichier de sortie",
    )
    parser.add_argument(
        "--full_dataset",
        action="store_true",
        help="Garder toutes les colonnes (défaut: sélection des colonnes pertinentes)",
    )
    args = parser.parse_args()

    print(f"\n=== Chargement des données === {args.data_dir}")
    df = load_application_train(data_dir=args.data_dir)
    print(f"Shape: {df.shape}")
    print(f"Valeurs manquantes: {df.isnull().sum().sum()}")

    # Sélection des colonnes pertinentes
    if not args.full_dataset:
        print(f"\n=== Sélection des colonnes ===")
        df = select_columns(df)
        print(f"Shape: {df.shape}")

    print(f"\n=== Preprocessing ===")
    df = preprocess_data(df)
    print(f"Shape: {df.shape}")
    print(f"Valeurs manquantes: {df.isnull().sum().sum()}")

    print(f"\n=== Sauvegarde ===")
    save_processed_data(df, filename=args.output_filename, data_dir=args.data_dir)
    print("Terminé!")


if __name__ == "__main__":
    main()
