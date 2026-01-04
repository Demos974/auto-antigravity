# Guide de Diagnostic et Dépannage pour Antigravity IDE

Ce guide vous aide à résoudre les problèmes courants lors de l'utilisation d'Auto-Antigravity avec l'IDE Antigravity de Google.

## 🔍 Diagnostic Rapide

### Étape 1 : Vérifier l'Extension

**Symptôme** : L'extension ne s'affiche pas dans la barre d'activité (gauche)

**Diagnosic** :
1. Ouvrir VS Code / Antigravity
2. Presser `Ctrl+Shift+X` pour ouvrir le panneau Extensions
3. Chercher "Auto-Antigravity"
4. Vérifier que l'extension est :
   - ✅ **Activé** : Icône visible
   - ❌ **Désactivé** : Cliquez sur "Enable"

**Action corrective** : Cliquez sur "Reload" si l'extension est chargée

---

### Étape 2 : Vérifier la Barre de Statut

**Symptôme** : L'indicateur "AA: Ready" n'apparaît pas en bas à droite

**Diagnosic** :
1. Regarder la barre de statut en bas à droite
2. Vous devriez voir "$(info) AA: Ready" ou "$(error) AA: Error"

**Action corrective** :
- Si vous voyez "$(error)" : Il y a un problème (voir Étape 3)

---

### Étape 3 : Consulter le Canal de Sortie

**Symptôme** : Erreurs ou avertissements non visibles

**Diagnosic** :
1. Presser `Ctrl+Shift+U` pour ouvrir le panneau Output
2. Sélectionner "Auto-Antigravity" dans le menu déroulant
3. Lire les messages d'erreur

**Messages d'erreur courants** :
- `ERREUR lors du chargement de l'extension` : Problème d'installation
- `Python non trouvé` : Le processus backend ne démarre pas
- `Connection refusée` : Impossible de communiquer avec le processus Python
- `Permission refusée` : Problème d'accès aux fichiers

---

## 🐛 Problèmes Connus et Solutions

### Problème 1 : Extension Non Activée

**Symptôme** :
- L'icône Auto-Antigravity n'apparaît pas
- Le dashboard ne s'ouvre pas
- Aucune commande disponible dans la palette (`Ctrl+Shift+P`)

**Solutions** :

1. **Redémarrer VS Code/Antigravity** :
   - Fermez complètement l'IDE
   - Rouvrez-le

2. **Réinstaller l'extension** :
   - `Ctrl+Shift+X` → Extensions
   - Cliquez sur les ... près d'Auto-Antigravity
   - Cliquez sur "Disable"
   - Cliquez sur "Enable"

3. **Vérifier le fichier VSIX** :
   - Le package `.vsix` est-il corrompu ?
   - Supprimez et réinstallez l'extension

4. **Vérifier les logs** :
   - Ouvrez `Ctrl+Shift+U` → Output → Auto-Antigravity
   - Cherchez des erreurs lors de l'activation

---

### Problème 2 : Processus Python Ne Démarre Pas

**Symptôme** :
- Aucune sortie dans le canal Output
- Le dashboard reste vide ou ne se met pas à jour
- Erreur "Python non trouvé" dans les logs

**Causes possibles** :
- Python n'est pas installé
- Python n'est pas dans le PATH
- Le chemin Python configuré est incorrect

**Solutions** :

1. **Vérifier l'installation de Python** :
```bash
python --version
```
   Vous devriez voir : `Python 3.x.x`

2. **Vérifier le chemin** :
```bash
where python
```
   Cela devrait retourner le chemin vers Python

3. **Configurer le chemin dans l'extension** :
   - `Ctrl+Shift+P` → "Settings"
   - Cherchez "autoAntigravity.pythonPath"
   - Entrez le chemin complet (ex: `C:\Python39\python.exe`)

4. **Pour Windows** :
   - Vérifiez que Python est dans les variables d'environnement
   - Settings → System → About → Environment variables

---

### Problème 3 : Erreur de Communication avec le Backend

**Symptôme** :
- Les commandes ne fonctionnent pas
- Le dashboard ne se rafraîchit pas
- Erreur "Connection refusée" dans les logs

**Solutions** :

1. **Vérifier que le processus Python tourne** :
```bash
# Dans un terminal séparé
tasklist | findstr python
```

2. **Vérifier les ports utilisés** :
```bash
# Vérifier si le port 8080 est déjà utilisé
netstat -ano | findstr :8080
```

3. **Tester la communication** :
   - Créez un fichier de test Python
   - Exécutez-le manuellement
   - Vérifiez les logs

4. **Redémarrer le processus** :
   - `Ctrl+Shift+P` → "Auto-Antigravity: Restart Language Server"
   - Cela redémarre le backend

---

### Problème 4 : Dashboard Ne S'Ouvre Pas

**Symptôme** :
- Cliquez sur l'icône mais rien ne se passe
- Le dashboard webview reste vide
- Erreur dans les logs

**Solutions** :

1. **Ouvrir manuellement le dashboard** :
   - `Ctrl+Shift+P` → "Auto-Antigravity: Show Dashboard"
   - Vérifiez si une erreur s'affiche

2. **Recharger la fenêtre** :
   - `Ctrl+Shift+P` → "Developer: Reload Window"
   - Cela recharge complètement l'extension

3. **Vérifier les erreurs webview** :
   - Clic droit dans le dashboard → "Inspect Element"
   - Regardez la console pour les erreurs JavaScript

4. **Désactiver/réactiver l'extension** :
   - `Ctrl+Shift+X` → Extensions → Auto-Antigravity → Disable
   - Puis réactivez

---

### Problème 5 : Mode Auto-Accept Ne Fonctionne Pas

**Symptôme** :
- Les actions ne sont pas automatisées
- Toujours demandé de confirmer
- L'état dans le dashboard reste sur "Désactivé"

**Solutions** :

1. **Vérifier la configuration** :
   - `Ctrl+Shift+P` → Settings
   - Cherchez "autoAntigravity.autoAccept.enabled"
   - Changez `false` → `true`

2. **Vérifier les règles** :
   - Certaines actions ne peuvent pas être acceptées automatiquement
   - Consultez les logs pour les raisons de rejet

3. **Toggle via commande** :
   - `Ctrl+Shift+P` → "Auto-Antigravity: Toggle Auto-Accept"
   - Vérifiez que l'état change

---

## 🔧 Outils de Diagnostic Avancés

### Vérifier l'État de l'Extension

Ouvrez le "Developer: Run Extension Development Host..." et exécutez :

```javascript
// Cela ouvre le backend Node.js de l'extension
```

**À rechercher** :
- Erreurs lors du chargement de `extension.js`
- Problèmes d'initialisation
- Erreurs d'enregistrement des commandes

### Activer le Mode Verbeux

Ouvrez les paramètres VS Code et activez :

```
"Auto-Antigravity › Troubleshoot: Verbose Logging"
```

**Ou** dans VS Code :
1. `Ctrl+Shift+P` → "Open Settings (JSON)"
2. Ajoutez : `"troubleshoot.verboseLogging": true`
3. Sauvegardez et rechargez

### Exporter les Logs

```bash
# Windows
type "%APPDATA%\Code\User\globalStorage\auto-antigravity\*.log" > desktop\auto-antigravity-logs.txt

# macOS
cp ~/Library/Application\Support/Code/User/globalStorage/auto-antigravity/*.log ~/Desktop/
```

---

## 📊 Vérifier les Métriques de Système

### Utilisation CPU/Mémoire Élevée

**Symptôme** :
- L'extension ralentit l'IDE
- CPU à 100% pendant l'utilisation
- Dégradations de performance

**Solutions** :

1. **Désactiver le rafraîchissement automatique** :
   - Settings → "autoAntigravity.monitoring.refreshInterval"
   - Augmentez l'intervalle (ex: de 5000ms à 30000ms)

2. **Réduire les fonctionnalités** :
   - Désactivez le monitoring si non nécessaire
   - Settings → "autoAntigravity.monitoring.enabled" → false

3. **Fermer le dashboard quand inutilisé** :
   - Le dashboard consomme de la mémoire
   - Fermez-le quand vous ne l'utilisez pas

### Problèmes de Mémoire

**Symptôme** :
- VS Code/Antigravity plante
- Erreur "Out of memory"
- Lenteur extrême

**Solutions** :

1. **Augmenter la mémoire allouée à VS Code** :
   - Créez/éditez `C:\Users\VOTRE_NOM\AppData\Roaming\Code\User\globalStorage\argv.json`
   - Modifiez `"max-memory"` (ex: `"max-memory": 8192` pour 8GB)

2. **Fermer d'autres instances** :
   - Plusieurs instances de VS Code consomment de la mémoire
   - Fermez tout sauf celle en cours d'utilisation

---

## 🌐 Problèmes de Réseau

### Proxy ou Firewall

**Symptôme** :
- L'extension ne peut pas télécharger de mises à jour
- Erreur de connexion avec les API externes
- Le dashboard ne charge pas les données

**Solutions** :

1. **Vérifier le proxy** :
```bash
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

2. **Ajouter des exceptions de firewall** :
   - Permettez l'accès à `localhost` (port 8080 ou autre)
   - Permettez l'accès aux ports nécessaires

3. **Désactiver le VPN si nécessaire** :
   - Certains VPN bloquent les communications locales

---

## 📝 Rapport de Bug

### Comment Signaler un Bug

1. **Collecter les informations** :
   - Version de l'extension (Settings → About)
   - Version d'Antigravity/VS Code
   - Version de Python
   - Système d'exploitation (Windows/macOS/Linux)

2. **Exporter les logs** :
```bash
# Ouvrir le panneau Output
Ctrl+Shift+U → Auto-Antigravity
# Copier les messages
Ctrl+A → Ctrl+C
```

3. **Créer un rapport détaillé** :
   - Description du problème
   - Étapes pour reproduire
   - Logs d'erreur
   - Capture d'écran (si applicable)
   - Configuration actuelle

4. **Signaler le bug** :
   - Via l'Extension : Vérifiez si il y a un lien "Report a bug"
   - Ou créez une issue sur GitHub (si publié)

### Format du Rapport de Bug

```markdown
## Bug Report

### Description
[Breve description du problème]

### Étapes pour Reproduire
1. [Étape 1]
2. [Étape 2]
3. ...

### Comportement Attendu
[Ce qui devrait se passer]

### Comportement Réel
[Ce qui se passe en réalité]

### Environnement

- **Version de l'extension** : 0.2.0
- **Version de VS Code/Antigravity** : [Version]
- **Version de Python** : [Version]
- **Système d'exploitation** : [Windows/macOS/Linux]

### Logs

```
[Collez les logs ici]
```

### Configuration

```json
{
  "autoAntigravity.monitoring.enabled": true,
  "autoAntigravity.monitoring.refreshInterval": 5000,
  "autoAntigravity.autoAccept.enabled": false,
  "autoAntigravity.pythonPath": "C:\\Python39\\python.exe"
}
```

### Capture d'Écran (si applicable)

[Attachez une capture]
```

---

## 🚀 Problèmes de Performance

### Extension Trop Lente

**Symptôme** :
- L'IDE devient lent après activation de l'extension
- Lag lors de la frappe
- Temps de réponse élevé

**Solutions** :

1. **Désactiver les fonctionnalités inutiles** :
   - Si vous n'utilisez pas le monitoring, désactivez-le
   - Désactivez le rafraîchissement automatique si trop fréquent

2. **Optimiser le rafraîchissement** :
   - Utilisez un intervalle plus long (ex: 30000ms au lieu de 5000ms)
   - Ne rafraîchissez que les données visibles

3. **Nettoyer le cache** :
   - Cache accumulé peut ralentir l'extension
   - `Ctrl+Shift+P` → "Auto-Antigravity: Clear Cache"

### Crash ou Gel

**Symptôme** :
- L'IDE plante fréquemment
- L'écran devient noir/glacé
- Extension non-réactive

**Solutions** :

1. **Activer le mode Safe** :
   - `Ctrl+Shift+P` → "Developer: Safe Mode"
   - Chargez l'extension sans exécution

2. **Vérifier les dépendances** :
   - Assurez-vous que tous les modules npm sont installés
   - `cd vscode-extension && npm install --force`

3. **Revenir à une version précédente** :
   - Désinstallez l'extension
   - Réinstallez la version 0.1.0 (si disponible)

---

## 📞 Ressources d'Aide

### Documentation

- **README Principal** : [README.md](../README.md)
- **Installation** : [EXTENSION_INSTALLATION.md](../EXTENSION_INSTALLATION.md)
- **Monitoring** : [docs/MONITORING_ARCHITECTURE.md](../docs/MONITORING_ARCHITECTURE.md)
- **GitHub** : [https://github.com/votre-username/auto-antigravity](https://github.com/votre-username/auto-antigravity)

### Communauté

- **GitHub Issues** : Signaler des bugs ou demander des fonctionnalités
- **GitHub Discussions** : Poser des questions
- **Stack Overflow** : Taguez vos questions avec `auto-antigravity`

---

## ✅ Checklist Avant de Signaler un Bug

Avant de signaler un problème, vérifiez :

- [ ] J'ai lu le guide de dépannage
- [ ] J'ai vérifié le canal de sortie pour les erreurs
- [ ] J'ai essayé de redémarrer VS Code/Antigravity
- [ ] J'ai vérifié que Python est installé et accessible
- [ ] J'ai vérifié mes paramètres de configuration
- [ ] J'ai exporté les logs de l'extension
- [ ] J'ai essayé de réinstaller l'extension
- [ ] J'ai vérifié que mon système répond aux prérequis

Si vous avez tout coché, vous êtes prêt à reporter un bug détaillé ! 🚀

---

## 📝 Mises à Jour du Guide

- **Version 1.0** (2024-01-04) : Création initiale avec diagnostic basique
- **Version 1.1** (Prochaine) : Ajout des diagnostics avancés

---

**💡 Astuce Pro** : Gardez ce fichier sous la main dans votre IDE pour un accès rapide aux solutions en cas de problème !
