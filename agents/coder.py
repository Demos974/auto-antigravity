"""
Agent Coder - Génère et modifie du code
"""
from typing import Dict, Any
from pathlib import Path
import json
from loguru import logger

from ..core.context import Context, Task, TaskStatus, AgentType
from ..models.base import BaseModel
from .planner import BaseAgent


class CoderAgent(BaseAgent):
    """Agent qui génère et modifie du code"""
    
    def __init__(self, model: BaseModel):
        super().__init__(model, "Coder")
        self.agent_type = AgentType.CODER
    
    async def execute(self, task: Task, context: Context) -> str:
        """Exécute une tâche de codage"""
        self._log_action("code_task", {"task_id": task.id, "description": task.description})
        
        # Générer le code
        code_files = await self._generate_code(task.description, context)
        
        # Écrire les fichiers
        files_created = []
        for file_path, content in code_files.items():
            await self._write_file(file_path, content, context)
            files_created.append(file_path)
        
        result_message = f"{len(files_created)} fichier(s) créé(s/modifié(s)): {', '.join(files_created)}"
        self._add_message(context, "assistant", result_message)
        
        return result_message
    
    async def _generate_code(self, task_description: str, context: Context) -> Dict[str, str]:
        """Génère le code en utilisant le modèle d'IA"""
        prompt = self._create_coding_prompt(task_description, context)
        
        response = await self.model.generate(
            prompt,
            temperature=0.3,
            max_tokens=4000
        )
        
        # Parser la réponse pour extraire les fichiers
        code_files = self._parse_code_response(response)
        
        return code_files
    
    def _create_coding_prompt(self, task_description: str, context: Context) -> str:
        """Crée le prompt pour la génération de code"""
        # Récupérer le contexte existant du projet
        existing_files = context.files_created + context.files_modified
        
        prompt = f"""Tu es un expert en développement logiciel. 
Ta tâche est de générer ou modifier du code selon la demande.

Description de la tâche:
{task_description}

Contexte du projet:
- Nom: {context.project_name}
- Description: {context.project_description}
- Chemin: {context.project_path}
- Fichiers existants: {', '.join(existing_files) if existing_files else 'Aucun'}

Génère le code nécessaire en suivant ces guidelines:
1. Utilise les meilleures pratiques de programmation
2. Ajoute des commentaires explicatifs
3. Structure le code de manière claire et modulaire
4. Utilise les technologies appropriées (par défaut: Python, JavaScript/TypeScript selon le contexte)

Format de réponse attendu (JSON):
{{
  "files": [
    {{
      "path": "chemin/relatif/du/fichier.ext",
      "content": "contenu du code..."
    }}
  ]
}}

IMPORTANT: Retourne UNIQUEMENT le JSON valide, sans autre texte."""
        
        return prompt
    
    def _parse_code_response(self, response: str) -> Dict[str, str]:
        """Parse la réponse du modèle pour extraire les fichiers de code"""
        import re
        
        code_files = {}
        
        # Essayer d'extraire le JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                files = data.get("files", [])
                
                for file_data in files:
                    file_path = file_data.get("path", "")
                    content = file_data.get("content", "")
                    if file_path and content:
                        code_files[file_path] = content
                
                return code_files
            
            except json.JSONDecodeError:
                logger.warning("Impossible de parser le JSON")
        
        # Fallback: créer un fichier à partir de la réponse
        code_files["output.txt"] = response
        
        return code_files
    
    async def _write_file(self, file_path: str, content: str, context: Context):
        """Écrit un fichier dans le projet"""
        try:
            from ..core.api_client import AntigravityClient
            
            # Essayer d'utiliser l'API Antigravity
            client = AntigravityClient()
            success = await client.write_file(file_path, content)
            
            if success:
                context.files_created.append(file_path)
                logger.info(f"Fichier créé via API: {file_path}")
            else:
                # Fallback: écrire directement
                self._write_file_locally(file_path, content, context)
        
        except Exception as e:
            logger.warning(f"Erreur avec l'API, écriture locale: {e}")
            self._write_file_locally(file_path, content, context)
    
    def _write_file_locally(self, file_path: str, content: str, context: Context):
        """Écrit un fichier localement"""
        project_path = Path(context.project_path)
        full_path = project_path / file_path
        
        # Créer les dossiers si nécessaire
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le fichier
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        context.files_created.append(file_path)
        logger.info(f"Fichier créé localement: {full_path}")
