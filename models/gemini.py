"""
Intégration avec Google Gemini
"""
from typing import Optional, Dict, Any, List
from loguru import logger

import warnings
# Suppress Google Gemini deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Google Generative AI non installé. Install avec: pip install google-generativeai")

from .base import BaseModel


class GeminiModel(BaseModel):
    """Client pour Google Gemini 3 Pro"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-3-pro"):
        super().__init__(api_key, model_name)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("google.generativeai n'est pas installé")
        
        self._validate_api_key()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client Gemini"""
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model_name)
        logger.info(f"Client Gemini initialisé avec le modèle {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération Gemini: {e}")
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
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            chat = self.client.start_chat(history=messages)
            response = await chat.send_message_async(
                messages[-1]["content"],
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec historique Gemini: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle"""
        return {
            "provider": "Google",
            "model": self.model_name,
            "available": GEMINI_AVAILABLE
        }
