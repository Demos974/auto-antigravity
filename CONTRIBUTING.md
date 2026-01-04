# Guide de Contribution

## Comment Contribuer

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer au projet Auto-Antigravity.

## Développement Local

1. **Fork le dépôt**
   ```bash
   git clone https://github.com/votre-username/auto-antigravity.git
   cd auto-antigravity
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Pour le développement
   ```

4. **Configurer les variables d'environnement**
   ```bash
   cp .env.example .env
   # Éditez .env avec vos clés API
   ```

## Structure du Code

```
auto-antigravity/
├── agents/          # Les agents spécialisés
├── core/            # Fonctionnalités principales
├── models/          # Intégration des modèles d'IA
└── utils/           # Utilitaires
```

## Créer un Nouvel Agent

Pour créer un nouvel agent :

1. Créez une nouvelle classe dans `agents/` qui hérite de `BaseAgent`
2. Implémentez la méthode `execute()`
3. Enregistrez l'agent dans `core/orchestrator.py`

Exemple :

```python
from .planner import BaseAgent
from ..core.context import Context, Task, AgentType

class MyCustomAgent(BaseAgent):
    def __init__(self, model):
        super().__init__(model, "MyCustom")
        self.agent_type = AgentType.CODER  # Ou un nouveau type
    
    async def execute(self, task: Task, context: Context) -> str:
        # Implémentez votre logique ici
        return "Résultat de l'exécution"
```

## Tester

Exécutez les tests :

```bash
pytest tests/
```

Avec coverage :

```bash
pytest --cov=auto_antigravity tests/
```

## Style de Code

Nous utilisons **Black** pour le formatage du code :

```bash
black .
```

Nous utilisons **flake8** pour la vérification de la qualité du code :

```bash
flake8 .
```

## Soumettre une Pull Request

1. Créez une branche pour votre feature
   ```bash
   git checkout -b feature/ma-nouvelle-feature
   ```

2. Commit vos changements
   ```bash
   git commit -m "Add: description de la feature"
   ```

3. Push et créez une PR
   ```bash
   git push origin feature/ma-nouvelle-feature
   ```

## Guidelines

- Écrivez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation si nécessaire
- Suivez le style de code existant
- Ajoutez des commentaires pour le code complexe

## Support

Pour toute question, ouvrez une Issue sur GitHub.
