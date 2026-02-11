#!/bin/bash

# Script pour lancer Jupyter Notebook avec l'environnement UV
# Utilisation: ./start_jupyter.sh

echo "🚀 Démarrage de Jupyter Notebook..."

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

# Démarrer Jupyter Notebook
echo "📓 Démarrage de Jupyter Notebook..."
echo "Le notebook sera accessible dans votre navigateur"
echo "Appuyez sur Ctrl+C pour arrêter Jupyter"
echo ""

uv run jupyter notebook notebooks/