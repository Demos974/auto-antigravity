# Guide d'Installation de l'Extension VS Code

Ce guide explique comment installer l'extension Auto-Antigravity dans VS Code ou Google Antigravity IDE.

## 📋 Prérequis

- **Node.js** (v14 ou supérieur)
  - Télécharger depuis https://nodejs.org/
  - Vérifier avec : `node --version`

- **VS Code** ou **Google Antigravity IDE**
  - Télécharger depuis https://code.visualstudio.com/
  - Ou depuis https://googleantigravityide.com/

- **Python** (pour le framework backend)
  - Télécharger depuis https://www.python.org/
  - Vérifier avec : `python --version`

## 🚀 Méthodes d'Installation

### Méthode 1: Script d'Installation Automatique (Recommandé) 🎯

#### Windows (PowerShell)

```powershell
# Exécuter le script PowerShell
.\install_extension.ps1
```

#### Linux/macOS (Bash)

```bash
# Rendre le script exécutable
chmod +x install_extension.sh

# Exécuter le script
./install_extension.sh
```

Le script va automatiquement :
1. ✅ Vérifier les prérequis
2. 📦 Installer les dépendances
3. 🔨 Compiler l'extension
4. 📦 Créer le package `.vsix`
5. 🚀 Installer dans VS Code

### Méthode 2: Installation Manuelle

#### Étape 1: Installer les dépendances

```bash
cd vscode-extension
npm install
```

#### Étape 2: Compiler l'extension

```bash
npm run compile
```

#### Étape 3: Créer le package

```bash
npm run package
```

Cela crée un fichier `.vsix` dans le dossier `vscode-extension`.

#### Étape 4: Installer dans VS Code

**Option A: Via la ligne de commande**

```bash
# Windows
code --install-extension auto-antigravity-x.x.x.vsix

# Linux/macOS
code --install-extension auto-antigravity-x.x.x.vsix
```

**Option B: Via l'interface VS Code**

1. Ouvrez VS Code
2. Appuyez sur `Ctrl+Shift+X` (Windows/Linux) ou `Cmd+Shift+X` (macOS)
3. Cliquez sur `...` (More Actions) dans le coin supérieur droit
4. Sélectionnez `Install from VSIX...`
5. Choisissez le fichier `.vsix` créé

### Méthode 3: Mode Développement

Pour le développement actif de l'extension :

```bash
cd vscode-extension
npm install
npm run watch
```

Puis dans VS Code :
1. `F5` ou `Debug → Start Debugging`
2. Cela ouvre une nouvelle fenêtre VS Code avec l'extension chargée

## ⚙️ Configuration de l'Extension

Une fois installée, configurez l'extension via les paramètres VS Code :

### Ouvrir les Paramètres

- `Ctrl+,` (Windows/Linux) ou `Cmd+,` (macOS)
- Ou : `Fichier → Préférences → Paramètres`
- Rechercher : `autoAntigravity`

### Paramètres Principaux

| Paramètre | Description | Défaut |
|-----------|-------------|----------|
| `autoAntigravity.pythonPath` | Chemin vers l'exécutable Python | `python` |
| `autoAntigravity.workspacePath` | Chemin du workspace de travail | `./workspace` |
| `autoAntigravity.monitoring.enabled` | Active le monitoring | `true` |
| `autoAntigravity.monitoring.refreshInterval` | Intervalle de rafraîchissement (ms) | `5000` |
| `autoAntigravity.cache.autoClean` | Active le nettoyage automatique | `true` |
| `autoAntigravity.cache.threshold` | Seuil de nettoyage (MB) | `500` |
| `autoAntigravity.autoAccept.enabled` | Active le mode Auto-Accept | `false` |

## 🎮 Utilisation de l'Extension

### Ouvrir le Dashboard

1. Cliquez sur l'icône **Auto-Antigravity** dans la barre d'activité (gauche)
2. Sélectionnez **Dashboard**
3. Le dashboard s'ouvre dans un panel intégré

### Exécuter une Tâche

- `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (macOS)
- Tapez : `Auto-Antigravity: Execute New Task`
- Entrez la description de la tâche
- L'extension exécute la tâche via le framework Python

### Activer le Mode Auto-Accept

- `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (macOS)
- Tapez : `Auto-Antigravity: Toggle Auto-Accept`
- Le statut s'affiche dans la barre de statut (en bas)

### Gérer le Cache

- Ouvrez le Dashboard → **Cache**
- Utilisez les boutons pour :
  - **Vider tout** : Supprimer toutes les entrées
  - **Auto-Clean** : Nettoyer automatiquement

### Exécuter les Diagnostics

- `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (macOS)
- Tapez : `Auto-Antigravity: Run Diagnostics`
- Les résultats s'affichent dans le canal de sortie

## 🐛 Dépannage

### L'extension ne s'active pas

1. Vérifiez que VS Code est redémarré après l'installation
2. Consultez le panneau **Problèmes** (`Ctrl+Shift+M`)
3. Vérifiez le canal de sortie **Auto-Antigravity** (`Ctrl+Shift+U`)

### Erreur "Python non trouvé"

1. Ouvrez les paramètres VS Code
2. Recherchez `autoAntigravity.pythonPath`
3. Entrez le chemin complet vers Python (ex: `C:\Python39\python.exe`)
4. Pour macOS/Linux: `/usr/local/bin/python3`

### L'extension plante au démarrage

1. Vérifiez les prérequis (Node.js, Python)
2. Réinstallez l'extension
3. Consultez le canal de sortie pour les messages d'erreur

### Le dashboard reste vide

1. Vérifiez que `autoAntigravity.monitoring.enabled` est activé
2. Vérifiez le canal de sortie pour les erreurs
3. Essayez de rafraîchir : `Ctrl+Shift+P` → `Refresh Dashboard`

## 📚 Documentation Complète

- **README principal** : [../README.md](../README.md)
- **Documentation monitoring** : [../docs/MONITORING_ARCHITECTURE.md](../docs/MONITORING_ARCHITECTURE.md)
- **Extension README** : [vscode-extension/README.md](vscode-extension/README.md)

## 🔗 Liens Utiles

- [VS Code Marketplace](https://marketplace.visualstudio.com/) - Pour les extensions officielles
- [Google Antigravity IDE](https://googleantigravityide.com/) - Environnement cible
- [Antigravity Panel](https://github.com/n2ns/antigravity-panel) - Extension d'inspiration

## 💡 Astuces

- Utilisez le **mode développement** (`F5`) pour tester rapidement les modifications
- Le canal de sortie `Auto-Antigravity` montre toutes les actions et erreurs
- Les paramètres peuvent être configurés par workspace ou globalement
- Le dashboard se rafraîchit automatiquement (configurable)

## 🤝 Contribution

Pour contribuer à l'extension :
1. Fork le projet
2. Apportez vos modifications
3. Testez en mode développement
4. Créez une Pull Request

## 📄 Licence

MIT License
