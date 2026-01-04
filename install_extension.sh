#!/bin/bash

# Script d'installation de l'extension Auto-Antigravity
# Pour Linux/macOS

echo "🚀 Installation de l'extension Auto-Antigravity pour VS Code / Antigravity IDE"
echo ""

# Vérifier Node.js est installé
echo "📦 Vérification de Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Veuillez l'installer depuis https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Node.js version: $NODE_VERSION"

# Aller dans le répertoire de l'extension
EXTENSION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/vscode-extension"
if [ ! -d "$EXTENSION_DIR" ]; then
    echo "❌ Répertoire d'extension non trouvé: $EXTENSION_DIR"
    exit 1
fi

cd "$EXTENSION_DIR"

# Installer les dépendances
echo ""
echo "📦 Installation des dépendances npm..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi
echo "✅ Dépendances installées"

# Compiler l'extension
echo ""
echo "🔨 Compilation de l'extension..."
npm run compile

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la compilation"
    exit 1
fi
echo "✅ Extension compilée avec succès"

# Vérifier VS Code est installé
echo ""
echo "🔍 Vérification de VS Code..."
if command -v code &> /dev/null; then
    CODE_PATH=$(which code)
    echo "✅ VS Code trouvé: $CODE_PATH"
elif command -v code-insiders &> /dev/null; then
    CODE_PATH=$(which code-insiders)
    echo "✅ VS Code Insiders trouvé: $CODE_PATH"
else
    echo "⚠️  VS Code n'est pas trouvé dans le PATH. Installation manuelle nécessaire."
    echo "   Vous pouvez installer l'extension via : Extensions → Install from VSIX..."
fi

# Créer le fichier .vsix
echo ""
echo "📦 Création du package .vsix..."
npm run package

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de la création du package"
    exit 1
fi

VSIX_FILE=$(ls -t *.vsix | head -n 1)
echo "✅ Package créé: $VSIX_FILE"

# Demander l'installation
echo ""
echo "🎉 Extension prête à être installée !"
echo ""

read -p "Voulez-vous installer l'extension maintenant ? (o/n) " install

if [ "$install" = "o" ] || [ "$install" = "O" ]; then
    if command -v code &> /dev/null || command -v code-insiders &> /dev/null; then
        echo "🚀 Installation en cours..."
        $CODE_PATH --install-extension "$VSIX_FILE"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Extension installée avec succès !"
            echo "   Redémarrez VS Code pour activer l'extension."
            echo ""
            echo "📚 Documentation: vscode-extension/README.md"
        else
            echo "❌ Erreur lors de l'installation"
        fi
    else
        echo "⚠️  VS Code n'est pas dans le PATH. Installation manuelle :"
        echo "   1. Ouvrez VS Code"
        echo "   2. Appuyez sur Ctrl+Shift+X pour ouvrir Extensions"
        echo "   3. Cliquez sur ... → Install from VSIX..."
        echo "   4. Sélectionnez: $EXTENSION_DIR/$VSIX_FILE"
    fi
else
    echo "📦 Package disponible: $EXTENSION_DIR/$VSIX_FILE"
    echo "   Installez-le manuellement via: Extensions → Install from VSIX..."
fi

echo ""
echo "✨ Installation terminée !"
