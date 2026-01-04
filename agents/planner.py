"""
Agent Planner - Planifie et décompose les tâches complexes
"""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from loguru import logger

try:
    from ..core.context import Context, Task, TaskStatus, AgentType
    from ..models.base import BaseModel
except ImportError:
    from core.context import Context, Task, TaskStatus, AgentType
    from models.base import BaseModel


class BaseAgent(ABC):
    """Classe de base pour tous les agents"""
    
    def __init__(self, model: BaseModel, name: str):
        self.model = model
        self.name = name
        self.agent_type = None
        self.auto_accept_manager = None

    def set_auto_accept_manager(self, manager):
        """Définit le gestionnaire d'auto-accept"""
        self.auto_accept_manager = manager
    
    @abstractmethod
    async def execute(self, task: Task, context: Context) -> str:
        """Exécute une tâche"""
        pass
    
    def _log_action(self, action: str, details: Dict[str, Any]):
        """Log une action"""
        logger.info(f"[{self.name}] {action}")
        context.add_action(action, details)
    
    def _add_message(self, context: Context, role: str, content: str):
        """Ajoute un message au contexte"""
        context.add_message(role, content, self.agent_type)


class PlannerAgent(BaseAgent):
    """Agent qui planifie et décompose les tâches"""
    
    def __init__(self, model: BaseModel):
        super().__init__(model, "Planner")
        self.agent_type = AgentType.PLANNER
    
    async def execute(self, task: Task, context: Context) -> str:
        """Exécute une tâche de planification"""
        self._log_action("plan_task", {"task_id": task.id, "description": task.description})
        
        # Générer le plan
        plan = await self._generate_plan(task.description, context)
        
        # Créer les sous-tâches
        subtasks = self._create_subtasks(plan, task.id)
        
        # Ajouter les sous-tâches au contexte
        for subtask in subtasks:
            context.tasks[subtask.id] = subtask
            task.subtasks.append(subtask.id)
        
        result_message = f"Plan généré avec {len(subtasks)} sous-tâches"
        self._add_message(context, "assistant", result_message)
        
        return result_message
    
    async def plan(self, task_description: str, context: Context) -> List[str]:
        """Planifie une tâche et retourne les IDs des sous-tâches"""
        plan = await self._generate_plan(task_description, context)
        subtasks = self._create_subtasks(plan, "main")
        
        for subtask in subtasks:
            context.tasks[subtask.id] = subtask
        
        return [st.id for st in subtasks]
    
    async def _generate_plan(self, task_description: str, context: Context) -> Dict[str, Any]:
        """Génère un plan en utilisant le modèle d'IA"""
        prompt = self._create_planning_prompt(task_description, context)
        
        response = await self.model.generate(
            prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parser la réponse pour extraire le plan
        plan = self._parse_plan_response(response)
        
        return plan
    
    def _create_planning_prompt(self, task_description: str, context: Context) -> str:
        """Crée le prompt pour la planification"""
        prompt = f"""Tu es un expert en planification de développement logiciel. 
Ta tâche est de décomposer la demande suivante en sous-tâches concrètes et réalisables.

Description de la tâche:
{task_description}

Contexte du projet:
- Nom: {context.project_name}
- Description: {context.project_description}
- Chemin: {context.project_path}

Génère un plan structuré avec:
1. Une liste de sous-tâches claires et spécifiques
2. Pour chaque sous-tâche, précise le type d'agent responsable:
   - "coder": pour générer/modifier du code
   - "tester": pour créer/exécuter des tests
   - "reviewer": pour revoir et valider le code
3. Les dépendances entre les sous-tâches si nécessaire

Format de réponse attendu (JSON):
{{
  "subtasks": [
    {{
      "description": "Description de la sous-tâche 1",
      "agent_type": "coder",
      "priority": 1,
      "dependencies": []
    }},
    {{
      "description": "Description de la sous-tâche 2",
      "agent_type": "tester",
      "priority": 2,
      "dependencies": ["1"]
    }}
  ]
}}"""
        
        return prompt
    
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse du modèle pour extraire le plan"""
        import json
        import re
        
        # Essayer d'extraire le JSON de la réponse
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                plan = json.loads(json_match.group())
                return plan
            except json.JSONDecodeError:
                logger.warning("Impossible de parser le JSON, tentative de parsing fallback")
        
        # Fallback: créer un plan simple
        return {
            "subtasks": [
                {
                    "description": response,
                    "agent_type": "coder",
                    "priority": 1,
                    "dependencies": []
                }
            ]
        }
    
    def _create_subtasks(self, plan: Dict[str, Any], parent_id: str) -> List[Task]:
        """Crée les objets Task à partir du plan"""
        subtasks = []
        subtasks_data = plan.get("subtasks", [])
        
        for i, st_data in enumerate(subtasks_data):
            task_id = f"{parent_id}_subtask_{i+1}"
            task = Task(
                id=task_id,
                description=st_data.get("description", ""),
                dependencies=st_data.get("dependencies", []),
                assigned_agent=AgentType(st_data.get("agent_type", "coder"))
            )
            subtasks.append(task)
        
        return subtasks
