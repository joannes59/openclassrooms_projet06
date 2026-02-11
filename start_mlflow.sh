#!/bin/bash

# Script pour lancer le serveur MLflow avec l'environnement UV
# Utilisation: ./start_mlflow.sh

echo "🚀 Démarrage du serveur MLflow..."

# Vérifier que UV est installé (vérifier plusieurs chemins possibles)
UV_CMD=""
if command -v uv &> /dev/null; then
    UV_CMD="uv"
elif [ -f "$HOME/.local/bin/uv" ]; then
    UV_CMD="$HOME/.local/bin/uv"
else
    echo "❌ UV n'est pas installé ou pas dans le PATH."
    echo "Essayez: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV trouvé: $UV_CMD"

# Vérifier si l'environnement virtuel existe
if [ ! -d ".venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    $UV_CMD venv
    
    echo "📚 Installation des dépendances..."
    source .venv/bin/activate
    $UV_CMD pip install -e .
else
    echo "✅ Environnement virtuel déjà existant"
fi


# Créer le répertoire pour les artefacts MLflow s'il n'existe pas
mkdir -p mlruns

# Démarrer le serveur MLflow
echo "🌐 Démarrage du serveur MLflow sur http://localhost:5000"
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

uv run mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --default-artifact-root ./mlruns \
    --backend-store-uri sqlite:///mlflow.db