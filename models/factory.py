"""
Factory pour créer des instances de modèles d'IA
"""
from typing import Optional, Dict, Any

from .base import BaseModel
from .gemini import GeminiModel
from .claude import ClaudeModel
from .openai import OpenAIModel


class ModelFactory:
    """Factory pour créer des modèles d'IA"""
    
    _models = {
        "gemini": GeminiModel,
        "claude": ClaudeModel,
        "openai": OpenAIModel
    }
    
    @classmethod
    def create_model(
        cls,
        model_type: str,
        api_key: str,
        model_name: Optional[str] = None
    ) -> BaseModel:
        """Crée une instance de modèle"""
        model_type = model_type.lower()
        
        if model_type not in cls._models:
            raise ValueError(f"Type de modèle non supporté: {model_type}. "
                           f"Types disponibles: {list(cls._models.keys())}")
        
        model_class = cls._models[model_type]
        
        # Noms de modèles par défaut
        default_names = {
            "gemini": "gemini-3-pro",
            "claude": "claude-sonnet-4.5",
            "openai": "gpt-4"
        }
        
        final_model_name = model_name or default_names[model_type]
        
        return model_class(api_key=api_key, model_name=final_model_name)
    
    @classmethod
    def create_from_config(cls, config: Dict[str, Any]) -> BaseModel:
        """Crée un modèle à partir d'une configuration"""
        return cls.create_model(
            model_type=config.get("type", "gemini"),
            api_key=config.get("api_key", ""),
            model_name=config.get("model_name")
        )
    
    @classmethod
    def register_model(cls, model_type: str, model_class: BaseModel):
        """Enregistre un nouveau type de modèle"""
        cls._models[model_type.lower()] = model_class
    
    @classmethod
    def available_models(cls) -> list:
        """Retourne la liste des modèles disponibles"""
        return list(cls._models.keys())
