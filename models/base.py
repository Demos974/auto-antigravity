"""
Classe de base pour les modèles d'IA
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseModel(ABC):
    """Classe de base pour tous les modèles d'IA"""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        pass
    
    @abstractmethod
    async def generate_with_history(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un historique de messages"""
        pass
    
    def _validate_api_key(self):
        """Valide que la clé API est présente"""
        if not self.api_key:
            raise ValueError(f"Clé API manquante pour le modèle {self.model_name}")
