import pandas as pd
from pathlib import Path


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

    raw_dir = data_dir / "raw"

    file_path = raw_dir / "application_train.csv"
    print(f"Chargement de {file_path}...")

    df = pd.read_csv(file_path)

    print(f"Shape: {df.shape}")
    print(f"Mémoire: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    return df


def load_application_test(data_dir=None):
    """
    Charge les données de test depuis application_test.csv
    """
    if data_dir is None:
        data_dir = Path.home() / "data"
    else:
        data_dir = Path(data_dir)

    raw_dir = data_dir / "raw"
    file_path = raw_dir / "application_test.csv"

    df = pd.read_csv(file_path)
    print(f"Test shape: {df.shape}")

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
    df = handle_missing_values(df)
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


if __name__ == "__main__":
    # Test
    df = load_application_train()
    print(f"\n=== Avant preprocessing ===")
    print(f"Shape: {df.shape}")
    print(f"Valeurs manquantes: {df.isnull().sum().sum()}")

    df = preprocess_data(df)
    print(f"\n=== Après preprocessing ===")
    print(f"Shape: {df.shape}")
    print(f"Valeurs manquantes: {df.isnull().sum().sum()}")

    # Sauvegarde au format parquet
    save_processed_data(df, "application_train_processed.parquet")
