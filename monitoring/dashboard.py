"""
Dashboard pour le monitoring des agents et des quotas
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger


class QuotaType(Enum):
    """Types de quotas"""
    THINKING = "thinking"  # Credits de raisonnement
    FLOW = "flow"          # Credits d'exécution


class ModelFamily(Enum):
    """Familles de modèles supportés"""
    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"


@dataclass
class ModelUsage:
    """Utilisation d'un modèle"""
    model_name: str
    family: ModelFamily
    thinking_credits_used: int = 0
    thinking_credits_limit: int = 0
    flow_credits_used: int = 0
    flow_credits_limit: int = 0
    requests_count: int = 0
    last_used: Optional[datetime] = None
    
    @property
    def thinking_percentage(self) -> float:
        """Pourcentage d'utilisation des credits de thinking"""
        if self.thinking_credits_limit == 0:
            return 0.0
        return (self.thinking_credits_used / self.thinking_credits_limit) * 100
    
    @property
    def flow_percentage(self) -> float:
        """Pourcentage d'utilisation des credits de flow"""
        if self.flow_credits_limit == 0:
            return 0.0
        return (self.flow_credits_used / self.flow_credits_limit) * 100
    
    @property
    def is_low_quota(self) -> bool:
        """Vérifie si le quota est bas (< 30%)"""
        return min(self.thinking_percentage, self.flow_percentage) < 30
    
    @property
    def is_critical_quota(self) -> bool:
        """Vérifie si le quota est critique (< 10%)"""
        return min(self.thinking_percentage, self.flow_percentage) < 10


@dataclass
class AgentStatus:
    """Statut d'un agent"""
    agent_name: str
    agent_type: str
    status: str  # "active", "idle", "error", "processing"
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_tasks: int = 0
    last_activity: Optional[datetime] = None
    error_message: Optional[str] = None
    current_task: Optional[str] = None
    
    @property
    def success_rate(self) -> float:
        """Taux de réussite"""
        if self.total_tasks == 0:
            return 0.0
        return (self.tasks_completed / self.total_tasks) * 100


@dataclass
class CacheEntry:
    """Entrée de cache"""
    task_id: str
    agent_type: str
    file_count: int = 0
    total_size: int = 0  # en octets
    created_at: datetime = field(default_factory=datetime.now)
    preview: Optional[str] = None
    
    @property
    def size_mb(self) -> float:
        """Taille en MB"""
        return self.total_size / (1024 * 1024)


@dataclass
class UsageHistory:
    """Historique d'utilisation"""
    timestamp: datetime
    model_family: ModelFamily
    thinking_credits: int
    flow_credits: int
    requests: int


class MonitoringDashboard:
    """Dashboard de monitoring pour les agents et quotas"""
    
    def __init__(self):
        # Statut des agents
        self.agents_status: Dict[str, AgentStatus] = {}
        
        # Utilisation des modèles
        self.models_usage: Dict[str, ModelUsage] = {}
        
        # Cache des tâches
        self.cache_entries: Dict[str, CacheEntry] = {}
        
        # Historique d'utilisation
        self.usage_history: List[UsageHistory] = []
        
        # Configuration
        self.warning_threshold = 30.0  # 30%
        self.critical_threshold = 10.0  # 10%
        self.history_max_days = 90
        
        # Mode Auto-Accept
        self.auto_accept_enabled = False
        
        logger.info("Dashboard de monitoring initialisé")
    
    def register_agent(self, agent_name: str, agent_type: str):
        """Enregistre un agent dans le monitoring"""
        if agent_name not in self.agents_status:
            self.agents_status[agent_name] = AgentStatus(
                agent_name=agent_name,
                agent_type=agent_type,
                status="idle"
            )
            logger.info(f"Agent {agent_name} ({agent_type}) enregistré dans le monitoring")
    
    def update_agent_status(
        self,
        agent_name: str,
        status: str,
        current_task: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Met à jour le statut d'un agent"""
        if agent_name in self.agents_status:
            agent_status = self.agents_status[agent_name]
            agent_status.status = status
            agent_status.last_activity = datetime.now()
            
            if current_task:
                agent_status.current_task = current_task
            
            if error_message:
                agent_status.error_message = error_message
                agent_status.status = "error"
            
            logger.debug(f"Statut agent {agent_name}: {status}")
    
    def increment_agent_tasks(self, agent_name: str, success: bool = True):
        """Incrémente les compteurs de tâches d'un agent"""
        if agent_name in self.agents_status:
            agent_status = self.agents_status[agent_name]
            agent_status.total_tasks += 1
            
            if success:
                agent_status.tasks_completed += 1
            else:
                agent_status.tasks_failed += 1
    
    def update_model_usage(
        self,
        model_name: str,
        family: ModelFamily,
        thinking_credits: int = 0,
        flow_credits: int = 0,
        thinking_limit: int = 0,
        flow_limit: int = 0
    ):
        """Met à jour l'utilisation d'un modèle"""
        if model_name not in self.models_usage:
            self.models_usage[model_name] = ModelUsage(
                model_name=model_name,
                family=family,
                thinking_credits_limit=thinking_limit,
                flow_credits_limit=flow_limit
            )
        
        usage = self.models_usage[model_name]
        usage.thinking_credits_used = thinking_credits
        usage.flow_credits_used = flow_credits
        usage.requests_count += 1
        usage.last_used = datetime.now()
        
        # Ajouter à l'historique
        history_entry = UsageHistory(
            timestamp=datetime.now(),
            family=family,
            thinking_credits=thinking_credits,
            flow_credits=flow_credits,
            requests=1
        )
        self.usage_history.append(history_entry)
        
        # Nettoyer l'historique trop ancien
        self._cleanup_history()
        
        logger.debug(f"Utilisation modèle {model_name}: {thinking_credits} thinking, {flow_credits} flow")
    
    def add_cache_entry(
        self,
        task_id: str,
        agent_type: str,
        file_count: int,
        total_size: int,
        preview: Optional[str] = None
    ):
        """Ajoute une entrée de cache"""
        self.cache_entries[task_id] = CacheEntry(
            task_id=task_id,
            agent_type=agent_type,
            file_count=file_count,
            total_size=total_size,
            preview=preview
        )
        logger.info(f"Entrée de cache ajoutée: {task_id} ({total_size / 1024 / 1024:.2f} MB)")
    
    def remove_cache_entry(self, task_id: str) -> bool:
        """Supprime une entrée de cache"""
        if task_id in self.cache_entries:
            del self.cache_entries[task_id]
            logger.info(f"Entrée de cache supprimée: {task_id}")
            return True
        return False
    
    def clear_all_cache(self) -> int:
        """Supprime tout le cache et retourne le nombre d'entrées supprimées"""
        count = len(self.cache_entries)
        self.cache_entries.clear()
        logger.info(f"{count} entrées de cache supprimées")
        return count
    
    def get_total_cache_size(self) -> int:
        """Retourne la taille totale du cache en octets"""
        return sum(entry.total_size for entry in self.cache_entries.values())
    
    def _cleanup_history(self):
        """Nettoie l'historique trop ancien"""
        cutoff_date = datetime.now() - timedelta(days=self.history_max_days)
        self.usage_history = [
            entry for entry in self.usage_history
            if entry.timestamp > cutoff_date
        ]
    
    def get_quota_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des quotas"""
        summary = {
            "models": [],
            "warnings": [],
            "critical": [],
            "total_thinking_used": 0,
            "total_thinking_limit": 0,
            "total_flow_used": 0,
            "total_flow_limit": 0
        }
        
        for model_name, usage in self.models_usage.items():
            model_info = {
                "name": model_name,
                "family": usage.family.value,
                "thinking_used": usage.thinking_credits_used,
                "thinking_limit": usage.thinking_credits_limit,
                "thinking_percentage": usage.thinking_percentage,
                "flow_used": usage.flow_credits_used,
                "flow_limit": usage.flow_credits_limit,
                "flow_percentage": usage.flow_percentage,
                "requests": usage.requests_count,
                "is_low": usage.is_low_quota,
                "is_critical": usage.is_critical_quota
            }
            
            summary["models"].append(model_info)
            summary["total_thinking_used"] += usage.thinking_credits_used
            summary["total_thinking_limit"] += usage.thinking_credits_limit
            summary["total_flow_used"] += usage.flow_credits_used
            summary["total_flow_limit"] += usage.flow_credits_limit
            
            if usage.is_critical_quota:
                summary["critical"].append(model_name)
            elif usage.is_low_quota:
                summary["warnings"].append(model_name)
        
        return summary
    
    def get_agents_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des agents"""
        summary = {
            "agents": [],
            "total_agents": len(self.agents_status),
            "active_agents": 0,
            "error_agents": 0,
            "idle_agents": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "total_tasks": 0
        }
        
        for agent_name, status in self.agents_status.items():
            agent_info = {
                "name": agent_name,
                "type": status.agent_type,
                "status": status.status,
                "tasks_completed": status.tasks_completed,
                "tasks_failed": status.tasks_failed,
                "total_tasks": status.total_tasks,
                "success_rate": status.success_rate,
                "last_activity": status.last_activity.isoformat() if status.last_activity else None,
                "current_task": status.current_task,
                "error_message": status.error_message
            }
            
            summary["agents"].append(agent_info)
            summary["total_tasks_completed"] += status.tasks_completed
            summary["total_tasks_failed"] += status.tasks_failed
            summary["total_tasks"] += status.total_tasks
            
            if status.status == "active":
                summary["active_agents"] += 1
            elif status.status == "error":
                summary["error_agents"] += 1
            elif status.status == "idle":
                summary["idle_agents"] += 1
        
        return summary
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """Retourne un résumé du cache"""
        total_size = self.get_total_cache_size()
        total_files = sum(entry.file_count for entry in self.cache_entries.values())
        
        # Regrouper par type d'agent
        by_agent_type = {}
        for entry in self.cache_entries.values():
            if entry.agent_type not in by_agent_type:
                by_agent_type[entry.agent_type] = {
                    "count": 0,
                    "size": 0,
                    "files": 0
                }
            by_agent_type[entry.agent_type]["count"] += 1
            by_agent_type[entry.agent_type]["size"] += entry.total_size
            by_agent_type[entry.agent_type]["files"] += entry.file_count
        
        return {
            "total_entries": len(self.cache_entries),
            "total_size_mb": total_size / (1024 * 1024),
            "total_files": total_files,
            "by_agent_type": {
                agent_type: {
                    "count": data["count"],
                    "size_mb": data["size"] / (1024 * 1024),
                    "files": data["files"]
                }
                for agent_type, data in by_agent_type.items()
            }
        }
    
    def get_usage_trends(self, minutes: int = 90) -> Dict[str, Any]:
        """Retourne les tendances d'utilisation"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_history = [
            entry for entry in self.usage_history
            if entry.timestamp > cutoff_time
        ]
        
        if not recent_history:
            return {"trends": []}
        
        # Regrouper par famille de modèle
        trends_by_family = {}
        for entry in recent_history:
            family = entry.family.value
            if family not in trends_by_family:
                trends_by_family[family] = {
                    "thinking_credits": [],
                    "flow_credits": [],
                    "timestamps": []
                }
            
            trends_by_family[family]["thinking_credits"].append(entry.thinking_credits)
            trends_by_family[family]["flow_credits"].append(entry.flow_credits)
            trends_by_family[family]["timestamps"].append(entry.timestamp.isoformat())
        
        return {
            "trends": [
                {
                    "family": family,
                    "thinking_credits": data["thinking_credits"],
                    "flow_credits": data["flow_credits"],
                    "timestamps": data["timestamps"]
                }
                for family, data in trends_by_family.items()
            ]
        }
    
    def get_full_dashboard_data(self) -> Dict[str, Any]:
        """Retourne toutes les données du dashboard"""
        return {
            "quota_summary": self.get_quota_summary(),
            "agents_summary": self.get_agents_summary(),
            "cache_summary": self.get_cache_summary(),
            "usage_trends": self.get_usage_trends(),
            "auto_accept_enabled": self.auto_accept_enabled,
            "timestamp": datetime.now().isoformat()
        }
    
    def toggle_auto_accept(self) -> bool:
        """Active/désactive le mode Auto-Accept"""
        self.auto_accept_enabled = not self.auto_accept_enabled
        logger.info(f"Mode Auto-Accept: {'activé' if self.auto_accept_enabled else 'désactivé'}")
        return self.auto_accept_enabled
    
    def set_thresholds(self, warning: float, critical: float):
        """Configure les seuils d'alerte"""
        self.warning_threshold = warning
        self.critical_threshold = critical
        logger.info(f"Seuils configurés: warning={warning}%, critical={critical}%")
