# Architecture du Module Monitoring

## Vue d'ensemble

Le module `monitoring` fournit un système complet de gestion et de monitoring des agents, inspiré par l'extension **[Antigravity Panel](https://github.com/n2ns/antigravity-panel)** pour Google Antigravity IDE.

## Composants

### 1. Dashboard (`monitoring/dashboard.py`)

**Objectif** : Centraliser et visualiser toutes les métriques des agents et quotas.

**Classes principales** :

#### `MonitoringDashboard`
Classe principale qui gère le monitoring en temps réel.

**Fonctionnalités** :
- Enregistrement des agents et suivi de leur statut
- Tracking de l'utilisation des modèles d'IA (Gemini, Claude, OpenAI)
- Gestion des quotas (Thinking Credits et Flow Credits)
- Historique d'utilisation avec tendances
- Alertes automatiques (warning à 30%, critique à 10%)

**Données trackingées** :
```python
- Agents: statut, tâches complétées/échouées, taux de réussite
- Modèles: crédits Thinking/Flow utilisés et limites
- Cache: nombre d'entrées, taille totale
- Historique: tendances d'utilisation sur 90 minutes
```

**Méthodes clés** :
- `register_agent(agent_name, agent_type)` - Enregistre un agent
- `update_agent_status(agent_name, status, current_task, error_message)` - Met à jour le statut
- `increment_agent_tasks(agent_name, success)` - Incrémente les compteurs
- `update_model_usage(...)` - Met à jour l'utilisation d'un modèle
- `get_quota_summary()` - Résumé des quotas
- `get_agents_summary()` - Résumé des agents
- `get_cache_summary()` - Résumé du cache
- `get_usage_trends(minutes)` - Tendances d'utilisation

### 2. Cache Manager (`monitoring/cache_manager.py`)

**Objectif** : Gérer le cache des tâches et conversations avec nettoyage automatique.

**Classes principales** :

#### `CacheConfig`
Configuration du cache avec :
- `auto_clean_enabled` : Activation du nettoyage automatique
- `auto_clean_threshold_mb` : Seuil de déclenchement (défaut: 500 MB)
- `auto_clean_keep_count` : Nombre d'entrées à conserver (défaut: 5)
- `max_age_days` : Âge maximum des entrées (défaut: 30 jours)

#### `CacheManager`
Gestionnaire du cache avec indexation et persistance.

**Fonctionnalités** :
- Création d'entrées de cache avec métadonnées
- Indexation persistante (JSON)
- Regroupement par type d'agent
- Nettoyage automatique basé sur la taille
- Nettoyage des entrées anciennes
- Prévisualisation du contenu avant suppression

**Structure du cache** :
```
cache/
├── cache_index.json           # Index persistant
├── task_1/                 # Entrée de cache
│   ├── file1.py
│   └── file2.txt
└── task_2/
    └── file3.js
```

**Méthodes clés** :
- `create_cache_entry(task_id, agent_type, files, preview)` - Crée une entrée
- `delete_cache_entry(task_id)` - Supprime une entrée
- `clear_all_cache()` - Supprime tout
- `auto_clean()` - Nettoyage automatique
- `cleanup_old_entries(max_age_days)` - Nettoyage des anciennes
- `get_statistics()` - Statistiques détaillées
- `preview_cache_entry(task_id)` - Prévisualisation

### 3. Auto-Accept Manager (`monitoring/auto_accept.py`)

**Objectif** : Automatiser l'acceptation des actions des agents avec règles de sécurité.

**Classes principales** :

#### `ActionType`
Types d'actions supportées :
- `FILE_WRITE` - Écriture de fichiers
- `TERMINAL_COMMAND` - Commandes terminal
- `CODE_GENERATION` - Génération de code
- `TEST_EXECUTION` - Exécution de tests
- `CODE_REVIEW` - Revue de code

#### `AutoAcceptRule`
Règle de configuration pour un type d'action :
- `enabled` - Activation
- `requires_confirmation` - Demande confirmation
- `max_file_size_mb` - Taille max des fichiers
- `allowed_patterns` - Motifs autorisés
- `blocked_patterns` - Motifs bloqués
- `custom_validator` - Fonction de validation personnalisée

#### `AutoAcceptManager`
Gestionnaire du mode Auto-Accept.

**Fonctionnalités** :
- Évaluation automatique des actions
- Règles configurables par type d'action
- Filtres de sécurité (regex patterns)
- Validateurs personnalisés
- Historique des actions avec statistiques

**Règles par défaut** :
```python
FILE_WRITE:
  - enabled: True
  - max_file_size_mb: 10
  - blocked: ["*.env", "*.key", "*secret*"]

TERMINAL_COMMAND:
  - enabled: False
  - requires_confirmation: True
  - blocked: ["rm -rf", "del /S /Q", "format", "mkfs"]

CODE_GENERATION:
  - enabled: True
  - max_file_size_mb: 5

TEST_EXECUTION:
  - enabled: True

CODE_REVIEW:
  - enabled: True
```

**Méthodes clés** :
- `toggle()` - Active/désactive
- `should_accept_action(action_type, action_data)` - Évalue une action
- `update_rule(action_type, rule)` - Met à jour une règle
- `get_statistics()` - Statistiques
- `get_recent_actions(limit)` - Actions récentes

### 4. Recovery Tools (`monitoring/recovery_tools.py`)

**Objectif** : Fournir des outils de récupération et diagnostics.

**Classes principales** :

#### `RecoveryTools`
Ensemble d'outils pour la récupération et le diagnostic.

**Fonctionnalités** :
- Redémarrage du Language Server
- Réinitialisation du cache de statut utilisateur
- Exécution de diagnostics complets
- Contrôle de santé du système
- Métriques système en temps réel
- Nettoyage des ressources obsolètes

**Méthodes clés** :
- `restart_language_server()` - Redémarre le Language Server
- `reset_status_cache()` - Réinitialise le cache de statut
- `run_diagnostics()` - Exécute les diagnostics
- `health_check()` - Contrôle de santé
- `get_system_metrics()` - Métriques système
- `cleanup_stale_resources()` - Nettoyage des ressources

**Diagnostics effectués** :
1. **Language Server** - Connexion et latence
2. **API Connection** - Connectivité et latence
3. **File System** - Accès et écriture
4. **Cache System** - Accessibilité

## Intégration avec l'Orchestrateur

L'orchestrateur intègre nativement le système de monitoring :

```python
orchestrator = Orchestrator(enable_monitoring=True)

# Accès au dashboard
dashboard_data = orchestrator.get_dashboard_data()
agents_summary = orchestrator.get_agents_summary()
quota_summary = orchestrator.get_quota_summary()

# Gestion du cache
cleaned = orchestrator.auto_clean_cache()
deleted = orchestrator.clear_cache()
entries = orchestrator.get_cache_entries()

# Mode Auto-Accept
enabled = orchestrator.toggle_auto_accept()
stats = orchestrator.get_auto_accept_stats()
actions = orchestrator.get_recent_actions()

# Outils de récupération
diagnostics = await orchestrator.run_diagnostics()
health = await orchestrator.health_check()
metrics = await orchestrator.get_system_metrics()
```

## Flux de Travail

### 1. Enregistrement d'un Agent

```python
orchestrator.register_agent(AgentType.CODER, coder_agent)
# ↓
# Le dashboard enregistre automatiquement l'agent
dashboard.register_agent("Coder", "coder")
```

### 2. Exécution d'une Tâche avec Monitoring

```python
# Avant l'exécution
orchestrator.dashboard.update_agent_status(
    "Coder", 
    "processing", 
    current_task="Créer le fichier main.py"
)

# Exécution
result = await coder_agent.execute(task, context)

# Après l'exécution
orchestrator.dashboard.increment_agent_tasks("Coder", success=True)
```

### 3. Utilisation d'un Modèle d'IA

```python
# Utilisation du modèle
response = await model.generate(prompt, ...)

# Mise à jour du dashboard
orchestrator.dashboard.update_model_usage(
    model_name="gemini-3-pro",
    family=ModelFamily.GEMINI,
    thinking_credits=150,
    flow_credits=50,
    thinking_limit=1000,
    flow_limit=500
)
```

### 4. Mode Auto-Accept

```python
# Évaluer une action
action_data = {
    "file_path": "src/main.py",
    "file_size": 2048,
    "content": "..."
}

result = await orchestrator.auto_accept.should_accept_action(
    ActionType.FILE_WRITE,
    action_data
)

if result["accept"]:
    # Exécuter l'action automatiquement
    await write_file(...)
else:
    # Demander confirmation ou rejeter
    if result["requires_confirmation"]:
        confirm = await ask_user_confirmation()
        if confirm:
            await write_file(...)
```

### 5. Gestion du Cache

```python
# Créer une entrée de cache après une tâche
orchestrator.cache_manager.create_cache_entry(
    task_id="task_123",
    agent_type="coder",
    files={
        "main.py": generated_code,
        "README.md": documentation
    },
    preview="Generated main.py with Flask app"
)

# Auto-clean automatique
orchestrator.cache_manager.auto_clean()
```

## Sécurité

### 1. Validation des Actions (Auto-Accept)

- **Patterns bloqués** : `*.env`, `*.key`, `*secret*`
- **Commandes dangereuses** : `rm -rf`, `del /S /Q`, `format`, `mkfs`
- **Limite de taille** : Configuration par type d'action
- **Validateurs personnalisés** : Possibilité d'ajouter des validateurs custom

### 2. Cache et Confidentialité

- **Données locales** : Tout est stocké localement
- **Index persistant** : JSON avec métadonnées
- **Nettoyage automatique** : Suppression après seuil
- **Suppression sécurisée** : Confirmation avant suppression

### 3. Alertes

- **Warning** : À 30% de quota restant
- **Critical** : À 10% de quota restant
- **Notifications** : Via logging et dashboard

## Configuration

### Dashboard Thresholds

```python
dashboard.warning_threshold = 30.0  # 30%
dashboard.critical_threshold = 10.0  # 10%
dashboard.history_max_days = 90
```

### Cache Configuration

```python
cache_config = CacheConfig(
    auto_clean_enabled=True,
    auto_clean_threshold_mb=500,
    auto_clean_keep_count=5,
    max_age_days=30,
    warning_threshold_mb=500,
    check_interval_seconds=120
)
```

### Auto-Accept Rules

```python
# Modifier une règle
rule = AutoAcceptRule(
    action_type=ActionType.FILE_WRITE,
    enabled=True,
    max_file_size_mb=20,  # Augmenter la limite
    allowed_patterns=["*.py", "*.js"],
    blocked_patterns=["*.env", "*.key"]
)

orchestrator.auto_accept.update_rule(ActionType.FILE_WRITE, rule)
```

## Exemples d'Utilisation

Voir `example_monitoring.py` pour un exemple complet de toutes les fonctionnalités.

## Références

- [Antigravity Panel](https://github.com/n2ns/antigravity-panel) - Inspiration principale
- [Google Antigravity IDE](https://googleantigravityide.com/) - Environnement cible
- [Auto-Claude](https://github.com/AndyMik90/Auto-Claude) - Framework d'inspiration

## Contribuer

Pour ajouter de nouvelles fonctionnalités de monitoring :

1. Créer une nouvelle classe dans `monitoring/`
2. Intégrer avec `MonitoringDashboard` si nécessaire
3. Exposer des méthodes dans `Orchestrator`
4. Ajouter des tests dans `tests/test_monitoring.py`
5. Documenter dans ce fichier et `README.md`
