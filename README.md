# Auto-Antigravity

Un framework de codage autonome multi-agents pour l'IDE Antigravity de Google, inspiré par [Auto-Claude](https://github.com/AndyMik90/Auto-Claude).

**🎨 NOUVEAU : Extension VS Code disponible pour une intégration directe !** Voir [EXTENSION_INSTALLATION.md](EXTENSION_INSTALLATION.md)

## 🚀 Fonctionnalités

### Système Multi-Agents
- **Planification Automatique** : L'agent Planner décompose les tâches complexes en sous-tâches
- **Génération de Code** : L'agent Coder génère et modifie le code
- **Validation** : L'agent Reviewer vérifie et valide le code généré
- **Tests Automatiques** : L'agent Tester exécute et analyse les tests

### Support Multi-Modèles
- **Google Gemini 3 Pro** : Par défaut pour la planification
- **Claude Sonnet 4.5** : Pour la génération et revue de code
- **OpenAI GPT-4** : Pour les tests et validation
- **Intégration Antigravity** : Utilise les API de l'IDE Antigravity

### 🎯 Monitoring Avancé (Inspiré d'Antigravity Panel)
- **Dashboard Complet** : Visualisation en temps réel de tous les agents et quotas
- **Gestion des Quotas** :
  - Tracking des crédits Thinking et Flow par modèle
  - Alertes automatiques (warning à 30%, critique à 10%)
  - Historique d'utilisation sur 90 minutes
- **Gestion du Cache** :
  - Visualisation des entrées de cache par agent
  - Nettoyage automatique avec seuil configurable
  - Prévisualisation du contenu avant suppression
- **Mode Auto-Accept** :
  - Automatisation des actions (écriture de fichiers, commandes terminal)
  - Règles configurables par type d'action
  - Filtres de sécurité (motifs bloqués/autorisés)
- **Outils de Récupération** :
  - Redémarrage du Language Server
  - Réinitialisation du cache de statut
  - Diagnostics complets (connectivité, fichiers, cache)
  - Contrôle de santé du système
  - Métriques système en temps réel (CPU, Mémoire, Disque)

## 📋 Prérequis

- Python 3.9+
- IDE Antigravity installé
- Clés API pour les modèles d'IA souhaités

## 🔧 Installation

```bash
# Cloner le projet
git clone https://github.com/votre-username/auto-antigravity.git
cd auto-antigravity

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos clés API
```

## 🚀 Utilisation

### Lancer le framework

```bash
python main.py
```

### Exemple de tâche

```python
from auto_antigravity import AutoAntigravity

# Initialiser le framework
aa = AutoAntigravity()

# Lancer une tâche
result = await aa.execute_task(
    description="Créer une application web de gestion de tâches",
    project_path="./my_project"
)
```

### 📊 Utilisation du Monitoring

```python
# Accéder au Dashboard complet
dashboard = aa.orchestrator.get_dashboard_data()

# Résumé des agents
agents = aa.orchestrator.get_agents_summary()

# Résumé des quotas
quotas = aa.orchestrator.get_quota_summary()

# Gestion du cache
cleaned = aa.orchestrator.auto_clean_cache()
deleted = aa.orchestrator.clear_cache()
entries = aa.orchestrator.get_cache_entries()

# Mode Auto-Accept
enabled = aa.orchestrator.toggle_auto_accept()
stats = aa.orchestrator.get_auto_accept_stats()
actions = aa.orchestrator.get_recent_actions(limit=50)

# Outils de récupération
diagnostics = await aa.orchestrator.run_diagnostics()
health = await aa.orchestrator.health_check()
metrics = await aa.orchestrator.get_system_metrics()
```

Pour un exemple complet, exécutez :
```bash
python example_monitoring.py
```

## 🏗️ Architecture

```
auto-antigravity/
├── agents/              # Agents spécialisés
│   ├── planner.py      # Planification des tâches
│   ├── coder.py        # Génération de code
│   ├── reviewer.py     # Revue de code
│   └── tester.py       # Exécution des tests
├── core/               # Fonctionnalités principales
│   ├── orchestrator.py # Orchestration des agents avec monitoring intégré
│   ├── context.py      # Gestion du contexte
│   └── api_client.py   # Client API Antigravity
├── monitoring/          # Système de monitoring avancé 🆕
│   ├── dashboard.py    # Dashboard complet des agents et quotas
│   ├── cache_manager.py # Gestion du cache avec auto-clean
│   ├── auto_accept.py  # Mode Auto-Accept configurable
│   └── recovery_tools.py # Outils de récupération et diagnostics
├── models/             # Intégration des modèles d'IA
│   ├── base.py         # Classe de base pour les modèles
│   ├── factory.py      # Factory pour créer les modèles
│   ├── gemini.py       # Google Gemini
│   ├── claude.py       # Anthropic Claude
│   └── openai.py       # OpenAI GPT
├── utils/              # Utilitaires
│   └── logger.py       # Logging configuré
└── config.py           # Configuration Pydantic
```

## 📝 Configuration

Les modèles d'IA supportés sont configurés dans `config.py` :

- **Gemini 3 Pro** : Par défaut pour Antigravity
- **Claude Sonnet 4.5** : Pour la génération de code
- **GPT-OSS** : Pour les tests et validation

## 🔐 Sécurité

- Sauvegardes automatiques avant les modifications
- Validation des fichiers avant écriture
- Sandbox pour l'exécution des tests
- Permissions restreintes pour les agents

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez soumettre une Pull Request ou ouvrir une Issue.

## 📄 Licence

MIT License

## 🙏 Remerciements

- [Auto-Claude](https://github.com/AndyMik90/Auto-Claude) - Inspiration
- [Google Antigravity IDE](https://googleantigravityide.com/) - Environnement cible
