# Changelog

Tous les changements notables seront documentés dans ce fichier.

## [0.2.0] - 2024-01-04

### Ajouté 🎉
- **Système de Monitoring Avancé** (inspiré d'Antigravity Panel) :
  - Dashboard complet pour visualiser en temps réel les agents et quotas
  - Gestion des quotas avec tracking des crédits Thinking et Flow
  - Alertes automatiques (warning à 30%, critique à 10%)
  - Historique d'utilisation sur 90 minutes
  - Métriques détaillées par modèle et famille
- **Gestion du Cache Intelligent** :
  - Visualisation des entrées de cache par agent
  - Nettoyage automatique avec seuil configurable
  - Prévisualisation du contenu avant suppression
  - Nettoyage des entrées anciennes
  - Statistiques détaillées (taille, nombre de fichiers, âge)
- **Mode Auto-Accept** :
  - Automatisation des actions (écriture de fichiers, commandes terminal)
  - Règles configurables par type d'action
  - Filtres de sécurité (motifs bloqués/autorisés)
  - Validateurs personnalisables
  - Historique des actions avec statistiques
- **Outils de Récupération** :
  - Redémarrage du Language Server
  - Réinitialisation du cache de statut utilisateur
  - Diagnostics complets (connectivité, fichiers, cache)
  - Contrôle de santé du système
  - Métriques système en temps réel (CPU, Mémoire, Disque)
  - Nettoyage des ressources obsolètes

### Amélioré
- Orchestrateur avec monitoring intégré activé par défaut
- API étendue pour accéder aux fonctionnalités de monitoring
- Documentation complète avec exemples d'utilisation
- Architecture modulaire pour faciliter l'extension

### Ajouté
- `monitoring/dashboard.py` - Dashboard de monitoring
- `monitoring/cache_manager.py` - Gestionnaire de cache
- `monitoring/auto_accept.py` - Mode Auto-Accept
- `monitoring/recovery_tools.py` - Outils de récupération
- `example_monitoring.py` - Exemple complet d'utilisation du monitoring

## [0.1.0] - 2024-01-04

### Ajouté
- Framework multi-agents initial
- Agent Planner pour la planification des tâches
- Agent Coder pour la génération de code
- Agent Reviewer pour la revue de code
- Agent Tester pour l'exécution des tests
- Support pour Google Gemini 3 Pro
- Support pour Claude Sonnet 4.5
- Support pour OpenAI GPT-4
- Client API pour l'IDE Antigravity
- Orchestrateur pour coordonner les agents
- Système de gestion de contexte
- Logging configuré avec loguru
- Configuration avec Pydantic Settings
- Interface CLI avec Typer
- Documentation README complète
- Guide de contribution
