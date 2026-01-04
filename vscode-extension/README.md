# Auto-Antigravity Extension

Extension VS Code pour l'intégration du framework Auto-Antigravity dans l'IDE Google Antigravity.

## 🚀 Fonctionnalités

### Dashboard Intégré
- Vue d'ensemble des agents et de leur statut
- Monitoring en temps réel des quotas
- Visualisation du cache avec gestion
- Graphiques de tendances d'utilisation

### Gestion des Agents
- Suivi de l'activité de chaque agent
- Taux de réussite par agent
- Historique des tâches complétées

### Gestion du Cache
- Visualisation des entrées de cache
- Nettoyage automatique avec seuil configurable
- Prévisualisation avant suppression
- Suppression manuelle ou automatique

### Mode Auto-Accept
- Automatisation des actions des agents
- Règles configurables par type d'action
- Filtres de sécurité (patterns bloqués/autorisés)
- Statistiques détaillées des actions

### Outils de Récupération
- Diagnostics complets (Language Server, API, Fichiers, Cache)
- Contrôle de santé du système
- Métriques système en temps réel (CPU, Mémoire, Disque)
- Redémarrage du Language Server

## 📦 Installation

### Installation locale

1. **Compiler l'extension** :
```bash
cd vscode-extension
npm install
npm run compile
```

2. **Installer dans VS Code** :
   - Ouvrez VS Code
   - `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (macOS)
   - Sélectionnez `Extensions: Install from VSIX...`
   - Sélectionnez le fichier `vscode-extension.vsix`

3. **Installer via commande** :
```bash
code --install-extension vscode-extension.vsix
```

### Installation en développement

```bash
cd vscode-extension
npm install
code --extensionDevelopmentPath=$PWD
```

## ⚙️ Configuration

L'extension peut être configurée via les paramètres VS Code (`Ctrl+,`) :

### Général
- `autoAntigravity.pythonPath` : Chemin vers Python (défaut: `python`)
- `autoAntigravity.workspacePath` : Chemin du workspace (défaut: `./workspace`)

### Monitoring
- `autoAntigravity.monitoring.enabled` : Active le monitoring (défaut: `true`)
- `autoAntigravity.monitoring.refreshInterval` : Intervalle de rafraîchissement en ms (défaut: `5000`)

### Cache
- `autoAntigravity.cache.autoClean` : Active le nettoyage automatique (défaut: `true`)
- `autoAntigravity.cache.threshold` : Seuil de nettoyage en MB (défaut: `500`)

### Auto-Accept
- `autoAntigravity.autoAccept.enabled` : Active le mode Auto-Accept (défaut: `false`)

## 🎮 Commandes Disponibles

Toutes les commandes sont accessibles via `Ctrl+Shift+P` (Windows/Linux) ou `Cmd+Shift+P` (macOS) :

| Commande | Description |
|-----------|-------------|
| `Auto-Antigravity: Refresh Dashboard` | Rafraîchit le dashboard |
| `Auto-Antigravity: Open Settings` | Ouvre les paramètres |
| `Auto-Antigravity: Toggle Auto-Accept` | Active/désactive Auto-Accept |
| `Auto-Antigravity: Clear All Cache` | Vide tout le cache |
| `Auto-Antigravity: Auto-Clean Cache` | Nettoie automatiquement le cache |
| `Auto-Antigravity: Run Diagnostics` | Exécute les diagnostics |
| `Auto-Antigravity: Health Check` | Effectue un contrôle de santé |
| `Auto-Antigravity: Show System Metrics` | Affiche les métriques système |
| `Auto-Antigravity: Restart Language Server` | Redémarre le Language Server |
| `Auto-Antigravity: Execute New Task` | Exécute une nouvelle tâche |

## 📊 Dashboard

Le dashboard s'ouvre dans un panel webview intégré à VS Code et affiche :

### Vue d'ensemble
- Statut du système
- Nombre d'agents actifs
- État du cache

### Agents
- Statut de chaque agent (Idle, Active, Error)
- Tâches complétées/échouées
- Taux de réussite

### Cache
- Nombre d'entrées
- Taille totale
- Boutons pour vider ou auto-cleaner

### Quotas
- Utilisation des crédits Thinking et Flow
- Alertes automatiques (warning à 30%, critique à 10%)
- Historique d'utilisation

### Auto-Accept
- État d'activation
- Statistiques des actions traitées
- Taux d'acceptation

## 🔧 Développement

### Structure

```
vscode-extension/
├── src/
│   └── extension.ts          # Code principal de l'extension
├── assets/
│   └── logo.svg            # Logo de l'extension
├── package.json              # Manifeste de l'extension
├── tsconfig.json           # Configuration TypeScript
├── webpack.config.js        # Configuration Webpack
└── README.md              # Documentation
```

### Compiler

```bash
npm run compile
```

### Watch mode

```bash
npm run watch
```

### Linter

```bash
npm run lint
```

### Tester

```bash
npm test
```

### Package

```bash
npm run package
```

## 🐛 Dépannage

### L'extension ne démarre pas

1. Vérifiez que Python est installé et accessible via le chemin configuré
2. Vérifiez le canal de sortie `Auto-Antigravity` (`Ctrl+Shift+U` → Auto-Antigravity)
3. Vérifiez les paramètres de l'extension

### Le dashboard ne se rafraîchit pas

1. Vérifiez que `autoAntigravity.monitoring.enabled` est activé
2. Vérifiez que l'intervalle de rafraîchissement est correct
3. Appuyez sur `Ctrl+Shift+P` → `Auto-Antigravity: Refresh Dashboard`

### Le processus Python plante

1. Vérifiez les dépendances Python : `pip install -r ../requirements.txt`
2. Vérifiez les clés API dans le fichier `.env`
3. Consultez le canal de sortie pour les messages d'erreur

## 📝 Roadmap

- [ ] Intégration complète avec le Language Server d'Antigravity
- [ ] Support multi-projets
- [ ] Export des métriques
- [ ] Notifications push pour les alertes de quota
- [ ] Intégration avec les tests de VS Code
- [ ] Customisation avancée du dashboard

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez ouvrir une Issue ou une Pull Request.

## 📄 Licence

MIT License

## 🔗 Liens

- [Framework Principal](../)
- [Documentation](../docs/)
- [Antigravity Panel](https://github.com/n2ns/antigravity-panel)
