"""
Agent Reviewer - Revoit et valide le code généré
"""
from typing import Dict, Any, List
import json
from loguru import logger

try:
    from ..core.context import Context, Task, TaskStatus, AgentType
    from ..models.base import BaseModel
except ImportError:
    from core.context import Context, Task, TaskStatus, AgentType
    from models.base import BaseModel
from .planner import BaseAgent


class ReviewerAgent(BaseAgent):
    """Agent qui revoit et valide le code"""
    
    def __init__(self, model: BaseModel):
        super().__init__(model, "Reviewer")
        self.agent_type = AgentType.REVIEWER
    
    async def execute(self, task: Task, context: Context) -> str:
        """Exécute une tâche de revue"""
        self._log_action("review_task", {"task_id": task.id, "description": task.description})
        
        # Revoir le code
        review_result = await self.review(context)
        
        result_message = f"Revue terminée: {review_result['summary']}"
        self._add_message(context, "assistant", result_message)
        
        return result_message
    
    async def review(self, context: Context) -> Dict[str, Any]:
        """Revoit tout le code du projet"""
        all_files = context.files_created + context.files_modified
        
        if not all_files:
            return {
                "summary": "Aucun fichier à revoir",
                "issues": [],
                "suggestions": []
            }
        
        # Revoir chaque fichier
        all_issues = []
        all_suggestions = []
        
        for file_path in all_files:
            review = await self._review_file(file_path, context)
            all_issues.extend(review.get("issues", []))
            all_suggestions.extend(review.get("suggestions", []))
        
        return {
            "summary": f"{len(all_files)} fichier(s) revoiué(s), {len(all_issues)} problème(s) identifié(s)",
            "issues": all_issues,
            "suggestions": all_suggestions
        }
    
    async def _review_file(self, file_path: str, context: Context) -> Dict[str, Any]:
        """Revoit un fichier spécifique"""
        # Lire le contenu du fichier
        file_content = await self._read_file_content(file_path, context)
        
        if not file_content:
            return {
                "issues": [{"severity": "error", "message": f"Impossible de lire le fichier {file_path}"}],
                "suggestions": []
            }
        
        # Générer la revue
        prompt = self._create_review_prompt(file_path, file_content, context)
        
        response = await self.model.generate(
            prompt,
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parser la réponse
        review = self._parse_review_response(response)
        
        return review
    
    async def _read_file_content(self, file_path: str, context: Context) -> str:
        """Lit le contenu d'un fichier"""
        try:
            try:
                from ..core.api_client import AntigravityClient
            except ImportError:
                from core.api_client import AntigravityClient
            from pathlib import Path
            
            # Essayer l'API Antigravity
            client = AntigravityClient()
            content = await client.read_file(file_path)
            
            if content:
                return content
            
            # Fallback: lire localement
            project_path = Path(context.project_path)
            full_path = project_path / file_path
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            return ""
    
    def _create_review_prompt(self, file_path: str, file_content: str, context: Context) -> str:
        """Crée le prompt pour la revue"""
        prompt = f"""Tu es un expert en revue de code. 
Ta tâche est d'analyser le code suivant et d'identifier les problèmes potentiels.

Fichier: {file_path}
Projet: {context.project_name}
Description: {context.project_description}

Contenu du fichier:
```
{file_content[:3000]}  # Limite à 3000 caractères pour le prompt
```

Analyse le code et identifie:
1. Les bugs potentiels
2. Les problèmes de sécurité
3. Les problèmes de performance
4. Les violations des bonnes pratiques
5. Les suggestions d'amélioration

Format de réponse attendu (JSON):
{{
  "issues": [
    {{
      "severity": "low|medium|high|critical",
      "message": "Description du problème",
      "line": 10,
      "code": "Code concerné"
    }}
  ],
  "suggestions": [
    {{
      "message": "Suggestion d'amélioration",
      "line": 15
    }}
  ]
}}

IMPORTANT: Retourne UNIQUEMENT le JSON valide."""
        
        return prompt
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse la réponse du modèle pour extraire la revue"""
        import re
        
        review = {
            "issues": [],
            "suggestions": []
        }
        
        # Essayer d'extraire le JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                review["issues"] = data.get("issues", [])
                review["suggestions"] = data.get("suggestions", [])
                return review
            except json.JSONDecodeError:
                logger.warning("Impossible de parser le JSON de la revue")
        
        return review
