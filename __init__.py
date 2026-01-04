"""
Auto-Antigravity - Framework multi-agents pour l'IDE Antigravity
"""
from .core.orchestrator import Orchestrator
from .core.context import Context, AgentType
from .models.factory import ModelFactory
from .agents.planner import PlannerAgent
from .agents.coder import CoderAgent
from .agents.reviewer import ReviewerAgent
from .agents.tester import TesterAgent
from .config import settings, create_directories
from .utils.logger import setup_logger, get_logger


__version__ = "0.1.0"
__author__ = "Auto-Antigravity Team"


class AutoAntigravity:
    """Interface principale pour Auto-Antigravity"""
    
    def __init__(self):
        """Initialise Auto-Antigravity"""
        setup_logger()
        create_directories()
        self.orchestrator = None
        self.logger = get_logger()
    
    async def initialize(
        self,
        gemini_api_key: str,
        anthropic_api_key: str,
        openai_api_key: str
    ):
        """Initialise les modèles et les agents"""
        self.logger.info("Initialisation d'Auto-Antigravity")
        
        # Créer les modèles
        planner_model = ModelFactory.create_model("gemini", gemini_api_key, "gemini-3-pro")
        coder_model = ModelFactory.create_model("claude", anthropic_api_key, "claude-sonnet-4.5")
        reviewer_model = ModelFactory.create_model("claude", anthropic_api_key, "claude-sonnet-4.5")
        tester_model = ModelFactory.create_model("openai", openai_api_key, "gpt-4")
        
        # Créer les agents
        planner = PlannerAgent(planner_model)
        coder = CoderAgent(coder_model)
        reviewer = ReviewerAgent(reviewer_model)
        tester = TesterAgent(tester_model)
        
        # Créer l'orchestrateur et enregistrer les agents
        from .core.api_client import AntigravityClient
        
        self.orchestrator = Orchestrator(AntigravityClient())
        self.orchestrator.register_agent(AgentType.PLANNER, planner)
        self.orchestrator.register_agent(AgentType.CODER, coder)
        self.orchestrator.register_agent(AgentType.REVIEWER, reviewer)
        self.orchestrator.register_agent(AgentType.TESTER, tester)
        
        self.logger.info("Auto-Antigravity initialisé avec succès")
    
    async def execute_task(
        self,
        task_description: str,
        project_path: str,
        project_name: str,
        project_description: str
    ) -> dict:
        """Exécute une tâche"""
        if not self.orchestrator:
            raise RuntimeError("Auto-Antigravity n'est pas initialisé. Appelez d'abord initialize()")
        
        # Initialiser le projet
        await self.orchestrator.initialize_project(
            project_path=project_path,
            project_name=project_name,
            project_description=project_description
        )
        
        # Exécuter la tâche
        result = await self.orchestrator.execute_task(task_description)
        
        return result
    
    def get_context(self):
        """Retourne le contexte actuel"""
        if self.orchestrator:
            return self.orchestrator.get_context()
        return None


# Fonction helper pour une utilisation rapide
async def auto_antigravity(
    task_description: str,
    project_path: str,
    project_name: str,
    project_description: str,
    gemini_api_key: str,
    anthropic_api_key: str,
    openai_api_key: str
) -> dict:
    """Fonction helper pour exécuter Auto-Antigravity"""
    aa = AutoAntigravity()
    
    await aa.initialize(gemini_api_key, anthropic_api_key, openai_api_key)
    
    return await aa.execute_task(
        task_description=task_description,
        project_path=project_path,
        project_name=project_name,
        project_description=project_description
    )
