"""
Orchestrateur principal pour coordonner les agents
"""
from typing import List, Optional
from pathlib import Path
from loguru import logger

from .context import Context, Task, TaskStatus, AgentType
from .api_client import AntigravityClient


class Orchestrator:
    """Orchestrateur qui coordonne les agents et gère le workflow"""
    
    def __init__(self, api_client: Optional[AntigravityClient] = None, enable_monitoring: bool = True):
        self.api_client = api_client or AntigravityClient()
        self.agents = {}
        self.context: Optional[Context] = None
        
        # Système de monitoring
        self.enable_monitoring = enable_monitoring
        self.dashboard = None
        self.cache_manager = None
        self.auto_accept = None
        self.recovery_tools = None
        
        if self.enable_monitoring:
            self._init_monitoring()
    
    def _init_monitoring(self):
        """Initialise le système de monitoring"""
        from ..monitoring.dashboard import MonitoringDashboard
        from ..monitoring.cache_manager import CacheManager, CacheConfig
        from ..monitoring.auto_accept import AutoAcceptManager
        from ..monitoring.recovery_tools import RecoveryTools
        
        # Initialiser le dashboard
        self.dashboard = MonitoringDashboard()
        
        # Initialiser le gestionnaire de cache
        cache_dir = Path("./cache")
        cache_config = CacheConfig(
            auto_clean_enabled=True,
            auto_clean_threshold_mb=500,
            auto_clean_keep_count=5
        )
        self.cache_manager = CacheManager(cache_dir, cache_config)
        
        # Initialiser le gestionnaire Auto-Accept
        self.auto_accept = AutoAcceptManager()
        
        # Initialiser les outils de récupération
        self.recovery_tools = RecoveryTools()
        
        logger.info("Système de monitoring initialisé")
    
    def register_agent(self, agent_type: AgentType, agent_instance):
        """Enregistre un agent dans l'orchestrateur"""
        self.agents[agent_type] = agent_instance
        
        # Enregistrer dans le dashboard si le monitoring est activé
        if self.enable_monitoring and self.dashboard:
            self.dashboard.register_agent(agent_instance.name, agent_type.value)
        
        logger.info(f"Agent {agent_type.value} enregistré")
    
    async def initialize_project(
        self,
        project_path: str,
        project_name: str,
        project_description: str
    ) -> Context:
        """Initialise un nouveau projet"""
        logger.info(f"Initialisation du projet: {project_name}")
        
        self.context = Context(
            project_path=project_path,
            project_name=project_name,
            project_description=project_description
        )
        
        # Vérifier la connexion avec Antigravity
        connected = await self.api_client.check_connection()
        if not connected:
            logger.warning("Impossible de se connecter à l'API Antigravity")
        
        return self.context
    
    async def execute_task(
        self,
        task_description: str,
        context: Optional[Context] = None
    ) -> dict:
        """Exécute une tâche complète"""
        if context:
            self.context = context
        
        if not self.context:
            raise ValueError("Context non initialisé")
        
        logger.info(f"Exécution de la tâche: {task_description}")
        self.context.add_message("system", task_description)
        
        # Créer la tâche principale
        main_task = Task(
            id="main",
            description=task_description,
            status=TaskStatus.IN_PROGRESS
        )
        self.context.tasks["main"] = main_task
        
        try:
            # Étape 1: Planification
            logger.info("Étape 1: Planification")
            planner = self.agents.get(AgentType.PLANNER)
            if planner:
                subtasks = await planner.plan(task_description, self.context)
                logger.info(f"{len(subtasks)} sous-tâches planifiées")
            
            # Étape 2: Exécution des sous-tâches
            logger.info("Étape 2: Exécution des sous-tâches")
            await self._execute_subtasks()
            
            # Étape 3: Revue
            logger.info("Étape 3: Revue du code")
            reviewer = self.agents.get(AgentType.REVIEWER)
            if reviewer:
                review_result = await reviewer.review(self.context)
                logger.info(f"Résultat de la revue: {review_result}")
            
            # Étape 4: Tests
            logger.info("Étape 4: Tests")
            tester = self.agents.get(AgentType.TESTER)
            if tester:
                test_results = await tester.test(self.context)
                logger.info(f"Tests terminés: {test_results}")
            
            # Marquer la tâche comme complétée
            self.context.update_task_status("main", TaskStatus.COMPLETED, "Tâche complétée avec succès")
            
            return {
                "success": True,
                "context": self.context.to_dict(),
                "message": "Tâche exécutée avec succès"
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la tâche: {e}")
            self.context.update_task_status("main", TaskStatus.FAILED, str(e))
            return {
                "success": False,
                "error": str(e),
                "context": self.context.to_dict()
            }
    
    async def _execute_subtasks(self):
        """Exécute toutes les sous-tâches en attente"""
        iteration = 0
        max_iterations = 10
        
        while iteration < max_iterations:
            pending_tasks = self.context.get_pending_tasks()
            
            if not pending_tasks:
                logger.info("Toutes les tâches sont complétées")
                break
            
            logger.info(f"Itération {iteration + 1}: {len(pending_tasks)} tâches en attente")
            
            for task in pending_tasks:
                if not task.assigned_agent:
                    continue
                
                agent = self.agents.get(task.assigned_agent)
                if not agent:
                    logger.warning(f"Agent {task.assigned_agent.value} non trouvé pour la tâche {task.id}")
                    continue
                
                try:
                    logger.info(f"Exécution de la tâche {task.id} par {task.assigned_agent.value}")
                    self.context.update_task_status(task.id, TaskStatus.IN_PROGRESS)
                    
                    result = await agent.execute(task, self.context)
                    
                    self.context.update_task_status(task.id, TaskStatus.COMPLETED, result)
                    logger.info(f"Tâche {task.id} complétée")
                
                except Exception as e:
                    logger.error(f"Erreur lors de l'exécution de la tâche {task.id}: {e}")
                    self.context.update_task_status(task.id, TaskStatus.FAILED, str(e))
            
            iteration += 1
            self.context.total_iterations = iteration
    
    def get_context(self) -> Optional[Context]:
        """Retourne le contexte actuel"""
        return self.context
    
    def reset(self):
        """Réinitialise l'orchestrateur"""
        self.context = None
        logger.info("Orchestrateur réinitialisé")
    
    # Méthodes de Monitoring
    
    def get_dashboard_data(self) -> dict:
        """Retourne toutes les données du dashboard"""
        if not self.enable_monitoring or not self.dashboard:
            return {"error": "Monitoring désactivé"}
        return self.dashboard.get_full_dashboard_data()
    
    def get_quota_summary(self) -> dict:
        """Retourne le résumé des quotas"""
        if not self.enable_monitoring or not self.dashboard:
            return {"error": "Monitoring désactivé"}
        return self.dashboard.get_quota_summary()
    
    def get_agents_summary(self) -> dict:
        """Retourne le résumé des agents"""
        if not self.enable_monitoring or not self.dashboard:
            return {"error": "Monitoring désactivé"}
        return self.dashboard.get_agents_summary()
    
    def get_cache_summary(self) -> dict:
        """Retourne le résumé du cache"""
        if not self.enable_monitoring or not self.cache_manager:
            return {"error": "Monitoring désactivé"}
        return self.cache_manager.get_statistics()
    
    def get_usage_trends(self, minutes: int = 90) -> dict:
        """Retourne les tendances d'utilisation"""
        if not self.enable_monitoring or not self.dashboard:
            return {"error": "Monitoring désactivé"}
        return self.dashboard.get_usage_trends(minutes)
    
    # Méthodes de Gestion du Cache
    
    def clear_cache(self) -> int:
        """Supprime tout le cache et retourne le nombre d'entrées supprimées"""
        if not self.enable_monitoring or not self.cache_manager:
            return 0
        return self.cache_manager.clear_all_cache()
    
    def auto_clean_cache(self) -> int:
        """Nettoie automatiquement le cache et retourne le nombre d'entrées supprimées"""
        if not self.enable_monitoring or not self.cache_manager:
            return 0
        return self.cache_manager.auto_clean()
    
    def get_cache_entries(self, agent_type: Optional[str] = None) -> list:
        """Retourne les entrées de cache"""
        if not self.enable_monitoring or not self.cache_manager:
            return []
        return self.cache_manager.list_cache_entries(agent_type)
    
    # Méthodes Auto-Accept
    
    def toggle_auto_accept(self) -> bool:
        """Active/désactive le mode Auto-Accept"""
        if not self.enable_monitoring or not self.auto_accept:
            return False
        return self.auto_accept.toggle()
    
    def set_auto_accept(self, enabled: bool):
        """Active ou désactive le mode Auto-Accept"""
        if self.enable_monitoring and self.auto_accept:
            self.auto_accept.set_enabled(enabled)
    
    def get_auto_accept_stats(self) -> dict:
        """Retourne les statistiques du mode Auto-Accept"""
        if not self.enable_monitoring or not self.auto_accept:
            return {"error": "Monitoring désactivé"}
        return self.auto_accept.get_statistics()
    
    def get_recent_actions(self, limit: int = 50) -> list:
        """Retourne les actions récentes"""
        if not self.enable_monitoring or not self.auto_accept:
            return []
        return self.auto_accept.get_recent_actions(limit)
    
    # Méthodes de Récupération
    
    async def restart_language_server(self) -> dict:
        """Redémarre le Language Server"""
        if not self.enable_monitoring or not self.recovery_tools:
            return {"error": "Monitoring désactivé"}
        return await self.recovery_tools.restart_language_server()
    
    async def reset_status_cache(self) -> dict:
        """Réinitialise le cache de statut"""
        if not self.enable_monitoring or not self.recovery_tools:
            return {"error": "Monitoring désactivé"}
        return await self.recovery_tools.reset_status_cache()
    
    async def run_diagnostics(self) -> dict:
        """Exécute les diagnostics"""
        if not self.enable_monitoring or not self.recovery_tools:
            return {"error": "Monitoring désactivé"}
        return await self.recovery_tools.run_diagnostics()
    
    async def health_check(self) -> dict:
        """Effectue un contrôle de santé"""
        if not self.enable_monitoring or not self.recovery_tools:
            return {"error": "Monitoring désactivé"}
        return await self.recovery_tools.health_check()
    
    async def get_system_metrics(self) -> dict:
        """Retourne les métriques système"""
        if not self.enable_monitoring or not self.recovery_tools:
            return {"error": "Monitoring désactivé"}
        return await self.recovery_tools.get_system_metrics()