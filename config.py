"""
Configuration principale pour Auto-Antigravity
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application"""
    
    # Clés API
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    antigravity_api_key: Optional[str] = None
    
    # API Antigravity
    antigravity_api_url: str = "http://localhost:8080"
    
    # Modèles par défaut
    default_model: str = "gemini-3-pro"
    coder_model: str = "claude-sonnet-4.5"
    tester_model: str = "gpt-oss"
    reviewer_model: str = "claude-sonnet-4.5"
    planner_model: str = "gemini-3-pro"
    
    # Configuration des Agents
    max_retries: int = 3
    timeout: int = 300
    max_iterations: int = 10
    max_concurrent_tasks: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/auto_antigravity.log"
    
    # Chemins
    workspace: Path = Path("./workspace")
    backup_dir: Path = Path("./backups")
    temp_dir: Path = Path("./temp")
    
    # Sécurité
    enable_sandbox: bool = True
    enable_backup: bool = True
    max_file_size: int = 10485760  # 10MB
    
    # Extensions de fichiers autorisées
    allowed_extensions: list = [
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".html", ".css", ".scss", ".json",
        ".md", ".txt", ".yaml", ".yml"
    ]
    
    # Fichiers/dossiers à ignorer
    ignore_patterns: list = [
        "node_modules", "__pycache__", ".git",
        "*.pyc", ".env", "*.log", "venv", ".venv"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instance globale de configuration
settings = Settings()


def get_settings() -> Settings:
    """Retourne l'instance de configuration"""
    return settings


def create_directories():
    """Crée les répertoires nécessaires"""
    settings.workspace.mkdir(parents=True, exist_ok=True)
    settings.backup_dir.mkdir(parents=True, exist_ok=True)
    settings.temp_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
