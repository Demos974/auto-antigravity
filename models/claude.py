"""
Intégration avec Anthropic Claude
"""
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic non installé. Install avec: pip install anthropic")

from .base import BaseModel


class ClaudeModel(BaseModel):
    """Client pour Anthropic Claude"""
    
    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4.5"):
        super().__init__(api_key, model_name)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic n'est pas installé")
        
        self._validate_api_key()
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client Claude"""
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        logger.info(f"Client Claude initialisé avec le modèle {self.model_name}")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Génère une réponse à partir d'un prompt"""
        try:
            message = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération Claude: {e}")
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
            # Convertir les messages au format Claude
            claude_messages = []
            for msg in messages[:-1]:  # Tous sauf le dernier
                claude_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Ajouter le dernier message
            claude_messages.append({
                "role": "user",
                "content": messages[-1]["content"]
            })
            
            message = await self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=claude_messages
            )
            
            return message.content[0].text
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec historique Claude: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le modèle"""
        return {
            "provider": "Anthropic",
            "model": self.model_name,
            "available": ANTHROPIC_AVAILABLE
        }
