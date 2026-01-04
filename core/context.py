"""
Gestion du contexte pour les agents
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Statuts possibles d'une tâche"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class AgentType(Enum):
    """Types d'agents disponibles"""
    PLANNER = "planner"
    CODER = "coder"
    REVIEWER = "reviewer"
    TESTER = "tester"


@dataclass
class Task:
    """Représente une tâche à accomplir"""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    assigned_agent: Optional[AgentType] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    result: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Context:
    """Contexte partagé entre les agents"""
    
    # Informations sur le projet
    project_path: str
    project_name: str
    project_description: str
    
    # Tâches
    tasks: Dict[str, Task] = field(default_factory=dict)
    current_task: Optional[str] = None
    
    # Historique des actions
    action_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # État du projet
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    
    # Métriques
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_iterations: int = 0
    
    # Messages et communication
    messages: List[Dict[str, str]] = field(default_factory=list)
    
    # Métadonnées
    started_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, agent: Optional[AgentType] = None):
        """Ajoute un message au contexte"""
        self.messages.append({
            "role": role,
            "content": content,
            "agent": agent.value if agent else None,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def add_action(self, action_type: str, details: Dict[str, Any]):
        """Ajoute une action à l'historique"""
        self.action_history.append({
            "type": action_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[str] = None):
        """Met à jour le statut d'une tâche"""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            self.tasks[task_id].updated_at = datetime.now()
            if result:
                self.tasks[task_id].result = result
            
            if status == TaskStatus.COMPLETED:
                self.tasks_completed += 1
            elif status == TaskStatus.FAILED:
                self.tasks_failed += 1
            
            self.updated_at = datetime.now()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Récupère une tâche par son ID"""
        return self.tasks.get(task_id)
    
    def get_pending_tasks(self) -> List[Task]:
        """Récupère toutes les tâches en attente"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
    
    def get_tasks_for_agent(self, agent_type: AgentType) -> List[Task]:
        """Récupère les tâches assignées à un agent spécifique"""
        return [
            task for task in self.tasks.values()
            if task.assigned_agent == agent_type and task.status == TaskStatus.PENDING
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le contexte en dictionnaire"""
        return {
            "project_path": self.project_path,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "tasks": {
                task_id: {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "dependencies": task.dependencies,
                    "subtasks": task.subtasks,
                    "assigned_agent": task.assigned_agent.value if task.assigned_agent else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "result": task.result,
                    "metadata": task.metadata
                }
                for task_id, task in self.tasks.items()
            },
            "action_history": self.action_history,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "files_deleted": self.files_deleted,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_iterations": self.total_iterations,
            "started_at": self.started_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
