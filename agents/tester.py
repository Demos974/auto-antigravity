"""
Agent Tester - Exécute et analyse les tests
"""
from typing import Dict, Any, List
import json
import subprocess
import asyncio
from pathlib import Path
from loguru import logger

try:
    from ..core.context import Context, Task, TaskStatus, AgentType
    from ..models.base import BaseModel
except ImportError:
    from core.context import Context, Task, TaskStatus, AgentType
    from models.base import BaseModel
from .planner import BaseAgent


class TesterAgent(BaseAgent):
    """Agent qui exécute et analyse les tests"""
    
    def __init__(self, model: BaseModel):
        super().__init__(model, "Tester")
        self.agent_type = AgentType.TESTER
    
    async def execute(self, task: Task, context: Context) -> str:
        """Exécute une tâche de test"""
        self._log_action("test_task", {"task_id": task.id, "description": task.description})
        
        # Exécuter les tests
        test_results = await self.test(context)
        
        result_message = f"Tests terminés: {test_results['summary']}"
        self._add_message(context, "assistant", result_message)
        
        return result_message
    
    async def test(self, context: Context) -> Dict[str, Any]:
        """Exécute les tests du projet"""
        project_path = Path(context.project_path)
        
        # Vérifier si des tests existent
        test_files = self._find_test_files(project_path)
        
        if not test_files:
            # Générer des tests
            logger.info("Aucun test trouvé, génération de tests...")
            test_generation_result = await self._generate_tests(context)
            
            if not test_generation_result["success"]:
                return {
                    "summary": "Échec de la génération de tests",
                    "tests_run": 0,
                    "tests_passed": 0,
                    "tests_failed": 0,
                    "details": []
                }
            
            test_files = self._find_test_files(project_path)
        
        # Exécuter les tests
        if self._is_python_project(project_path):
            test_results = await self._run_python_tests(project_path)
        elif self._is_javascript_project(project_path):
            test_results = await self._run_javascript_tests(project_path)
        else:
            test_results = {
                "summary": "Type de projet non supporté pour les tests automatiques",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "details": []
            }
        
        return test_results
    
    def _find_test_files(self, project_path: Path) -> List[str]:
        """Trouve les fichiers de tests dans le projet"""
        test_files = []
        
        # Python test files
        for py_file in project_path.rglob("test_*.py"):
            test_files.append(str(py_file))
        
        for py_file in project_path.rglob("*_test.py"):
            test_files.append(str(py_file))
        
        # JavaScript/TypeScript test files
        for js_file in project_path.rglob("*.test.js"):
            test_files.append(str(js_file))
        
        for ts_file in project_path.rglob("*.test.ts"):
            test_files.append(str(ts_file))
        
        return test_files
    
    async def _generate_tests(self, context: Context) -> Dict[str, Any]:
        """Génère des tests automatiquement"""
        prompt = self._create_test_generation_prompt(context)
        
        response = await self.model.generate(
            prompt,
            temperature=0.3,
            max_tokens=3000
        )
        
        # Parser la réponse pour extraire les tests
        test_files = self._parse_test_response(response)
        
        # Écrire les fichiers de tests
        files_created = 0
        for file_path, content in test_files.items():
            await self._write_test_file(file_path, content, context)
            files_created += 1
        
        return {
            "success": files_created > 0,
            "files_created": files_created
        }
    
    def _create_test_generation_prompt(self, context: Context) -> str:
        """Crée le prompt pour la génération de tests"""
        prompt = f"""Tu es un expert en tests logiciels. 
Ta tâche est de générer des tests unitaires pour le projet.

Projet:
- Nom: {context.project_name}
- Description: {context.project_description}
- Fichiers créés/modifiés: {', '.join(context.files_created + context.files_modified)}

Génère des tests unitaires complets qui:
1. Couvrent les fonctionnalités principales
2. Incluent des cas de test positifs et négatifs
3. Utilisent le framework de tests approprié (pytest pour Python, Jest pour JS/TS)

Format de réponse attendu (JSON):
{{
  "tests": [
    {{
      "path": "tests/test_example.py",
      "content": "contenu du fichier de test..."
    }}
  ]
}}

IMPORTANT: Retourne UNIQUEMENT le JSON valide."""
        
        return prompt
    
    def _parse_test_response(self, response: str) -> Dict[str, str]:
        """Parse la réponse du modèle pour extraire les tests"""
        import re
        
        test_files = {}
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                tests = data.get("tests", [])
                
                for test_data in tests:
                    file_path = test_data.get("path", "")
                    content = test_data.get("content", "")
                    if file_path and content:
                        test_files[file_path] = content
                
                return test_files
            except json.JSONDecodeError:
                logger.warning("Impossible de parser le JSON des tests")
        
        return test_files
    
    async def _write_test_file(self, file_path: str, content: str, context: Context):
        """Écrit un fichier de test"""
        try:
            project_path = Path(context.project_path)
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            context.files_created.append(file_path)
            logger.info(f"Test créé: {file_path}")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du test {file_path}: {e}")
    
    def _is_python_project(self, project_path: Path) -> bool:
        """Vérifie si c'est un projet Python"""
        return (project_path / "requirements.txt").exists() or \
               (project_path / "setup.py").exists() or \
               (project_path / "pyproject.toml").exists() or \
               any(project_path.rglob("*.py"))
    
    def _is_javascript_project(self, project_path: Path) -> bool:
        """Vérifie si c'est un projet JavaScript/TypeScript"""
        return (project_path / "package.json").exists() or \
               any(project_path.rglob("*.js")) or \
               any(project_path.rglob("*.ts"))
    
    async def _run_python_tests(self, project_path: Path) -> Dict[str, Any]:
        """Exécute les tests Python avec pytest"""
        try:
            # Exécuter pytest
            process = await asyncio.create_subprocess_exec(
                "python", "-m", "pytest",
                str(project_path),
                "--verbose",
                "--tb=short",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            stdout, stderr = await process.communicate()
            
            # Parser les résultats
            output = stdout.decode('utf-8')
            return self._parse_test_output(output)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des tests Python: {e}")
            return {
                "summary": f"Erreur: {str(e)}",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "details": []
            }
    
    async def _run_javascript_tests(self, project_path: Path) -> Dict[str, Any]:
        """Exécute les tests JavaScript/TypeScript avec Jest"""
        try:
            # Exécuter npm test
            process = await asyncio.create_subprocess_exec(
                "npm", "test",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=project_path
            )
            
            stdout, stderr = await process.communicate()
            
            # Parser les résultats
            output = stdout.decode('utf-8')
            return self._parse_test_output(output)
        
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des tests JS/TS: {e}")
            return {
                "summary": f"Erreur: {str(e)}",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "details": []
            }
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse la sortie des tests"""
        import re
        
        # Essayer d'extraire les statistiques
        # Pattern pour pytest: "X passed, Y failed"
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        total = passed + failed
        
        return {
            "summary": f"{total} test(s) exécuté(s), {passed} réussi(s), {failed} échoué(s)",
            "tests_run": total,
            "tests_passed": passed,
            "tests_failed": failed,
            "details": [{"output": output}]
        }
