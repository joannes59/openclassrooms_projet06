# Data Module

## Functionnalités à ajouter

### Exploration.py

Le fichier `exploration.py` doit générer un fichier CSV décrivant toutes les colonnes des dataframes sources.

**Colonnes du fichier CSV généré :**

| Colonne | Description |
|---------|-------------|
| name | Nom du champ (en anglais) |
| table | Nom du fichier source |
| dtype | Type de données |
| origin | Origine du champ (ex: original) |
| key | Clé (PRIMARY, FOREIGN, TARGET) |
| level | Niveau de données |
| nb_row | Nombre de lignes |
| unique | Nombre de valeurs uniques |
| notnull | Nombre de valeurs non manquantes |
| isna | Nombre de valeurs manquantes |
| mean | Moyenne (pour les numériques) |
| std | Écart-type (pour les numériques) |
| min | Valeur minimum (pour les numériques) |
| 25% | Premier quartile (pour les numériques) |
| 50% | Médiane (pour les numériques) |
| 75% | Troisième quartile (pour les numériques) |
| max | Valeur maximum (pour les numériques) |
| categ | Catégorie (BINARY, NUMERIC, CATEGORY) |
| categ_value | Valeur de la catégorie |
| p_value | Valeur p (pour les analyses statistiques) |
| correlation | Corrélation avec la cible |

**Style des noms de champs :** snake_case anglais (ex: `customer_id`, `order_date`, etc.)

**Objectif :** Permettre une analyse exploratoire rapide des données sources avant le preprocessing.
