# Data Module

## Functionnalités à ajouter

### Exploration.py

Le fichier `exploration.py` doit générer un fichier CSV décrivant toutes les colonnes des dataframes sources.

**Colonnes du fichier CSV généré :**

| Colonne | Description |
|---------|-------------|
| name | Nom du champ (en anglais) |
| file | Nom du fichier source |
| dtype | Type de données |
| description | Description textuelle du champ |
| unique | Nombre de valeurs uniques |
| notna | Nombre de valeurs non manquantes |
| mean | Moyenne (pour les numériques) |
| std | Écart-type (pour les numériques) |
| min | Valeur minimum (pour les numériques) |
| 25% | Premier quartile (pour les numériques) |
| 50% | Médiane (pour les numériques) |
| 75% | Troisième quartile (pour les numériques) |
| max | Valeur maximum (pour les numériques) |

**Style des noms de champs :** snake_case anglais (ex: `customer_id`, `order_date`, etc.)

**Objectif :** Permettre une analyse exploratoire rapide des données sources avant le preprocessing.
