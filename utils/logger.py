"""
Configuration du logging pour Auto-Antigravity
"""
import sys
from pathlib import Path
from loguru import logger

try:
    from ..config import settings
except ImportError:
    import sys
    import os
    sys.path.append(str(Path(__file__).parent.parent))
    from config import settings



def setup_logger():
    """Configure le système de logging"""
    # Supprimer le handler par défaut
    logger.remove()
    
    # Configuration de la console
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Configuration du fichier
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",
        retention="1 week",
        compression="zip"
    )
    
    logger.info("Système de logging initialisé")


def get_logger():
    """Retourne l'instance du logger"""
    return logger
