from .base import BaseModel
from typing import Dict, Any, List

class NullModel(BaseModel):
    """Modèle 'vide' utilisé quand aucune clé API n'est fournie."""
    
    def __init__(self, model_name: str = "Unconfigured"):
        super().__init__(api_key="none", model_name=model_name)
        
    async def generate(self, prompt: str, **kwargs) -> str:
        raise ValueError("Clé API manquante. Veuillez configurer vos clés dans le fichier .env.")
        
    async def generate_with_history(self, messages: list, **kwargs) -> str:
        raise ValueError("Clé API manquante. Veuillez configurer vos clés dans le fichier .env.")
        
    def get_usage(self) -> Dict[str, Any]:
        return {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}
