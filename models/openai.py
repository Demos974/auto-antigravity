"""
Intégration avec OpenAI
"""
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI non installé. Install avec: pip install openai")

from .base import BaseModel


class OpenAIModel(BaseModel):
    """Client pour OpenAI GPT"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        super().__init__(api_key, model_name)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("openai n'est pas installé")
        
        self._validate_api_key()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client OpenAI"""
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        logger.info(f"Client OpenAI initialisé avec le modèle {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {e}")
            raise
    
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un historique de messages"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec historique OpenAI: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle"""
        return {
            "provider": "OpenAI",
            "model": self.model_name,
            "available": OPENAI_AVAILABLE
        }
