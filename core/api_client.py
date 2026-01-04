"""
Client API pour l'IDE Antigravity de Google
"""
import httpx
from typing import Optional, Dict, Any, List
from pathlib import Path
import json
from loguru import logger

from ..config import settings


class AntigravityAPIError(Exception):
    """Exception pour les erreurs de l'API Antigravity"""
    pass


class AntigravityClient:
    """Client pour interagir avec l'API Antigravity"""
    
    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.api_url = api_url or settings.antigravity_api_url
        self.api_key = api_key or settings.antigravity_api_key
        self.timeout = settings.timeout
        
        if not self.api_key:
            logger.warning("Aucune clé API Antigravity fournie. Certaines fonctionnalités peuvent ne pas fonctionner.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Génère les en-têtes pour les requêtes API"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Effectue une requête à l'API Antigravity"""
        url = f"{self.api_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=self._get_headers())
                elif method == "POST":
                    response = await client.post(url, headers=self._get_headers(), json=data)
                elif method == "PUT":
                    response = await client.put(url, headers=self._get_headers(), json=data)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self._get_headers())
                else:
                    raise ValueError(f"Méthode HTTP non supportée: {method}")
                
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                logger.error(f"Erreur HTTP: {e.response.status_code} - {e.response.text}")
                raise AntigravityAPIError(f"Erreur API: {e.response.status_code}")
            except httpx.TimeoutException:
                logger.error("Timeout lors de la requête API")
                raise AntigravityAPIError("Timeout de la requête")
            except httpx.RequestError as e:
                logger.error(f"Erreur de requête: {e}")
                raise AntigravityAPIError(f"Erreur de connexion: {e}")
    
    # Méthodes pour les fichiers
    
    async def read_file(self, file_path: str) -> str:
        """Lit le contenu d'un fichier"""
        result = await self._make_request("GET", f"/files/read?path={file_path}")
        return result.get("content", "")
    
    async def write_file(self, file_path: str, content: str) -> bool:
        """Écrit du contenu dans un fichier"""
        data = {"path": file_path, "content": content}
        result = await self._make_request("POST", "/files/write", data)
        return result.get("success", False)
    
    async def list_files(self, directory: str) -> List[str]:
        """Liste les fichiers d'un répertoire"""
        result = await self._make_request("GET", f"/files/list?path={directory}")
        return result.get("files", [])
    
    async def delete_file(self, file_path: str) -> bool:
        """Supprime un fichier"""
        result = await self._make_request("DELETE", f"/files?path={file_path}")
        return result.get("success", False)
    
    # Méthodes pour l'éditeur
    
    async def get_cursor_position(self) -> Dict[str, int]:
        """Récupère la position du curseur"""
        result = await self._make_request("GET", "/editor/cursor")
        return {
            "line": result.get("line", 0),
            "column": result.get("column", 0)
        }
    
    async def open_file(self, file_path: str, line: int = 0) -> bool:
        """Ouvre un fichier dans l'éditeur"""
        data = {"path": file_path, "line": line}
        result = await self._make_request("POST", "/editor/open", data)
        return result.get("success", False)
    
    # Méthodes pour le terminal
    
    async def execute_command(self, command: str) -> Dict[str, Any]:
        """Exécute une commande dans le terminal"""
        data = {"command": command}
        result = await self._make_request("POST", "/terminal/execute", data)
        return {
            "exit_code": result.get("exit_code"),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", "")
        }
    
    # Méthodes pour l'intelligence artificielle
    
    async def get_ai_suggestion(self, context: str) -> str:
        """Obtient une suggestion de l'IA d'Antigravity"""
        data = {"context": context}
        result = await self._make_request("POST", "/ai/suggest", data)
        return result.get("suggestion", "")
    
    # Méthodes pour la gestion de projet
    
    async def get_project_info(self) -> Dict[str, Any]:
        """Récupère les informations du projet actuel"""
        result = await self._make_request("GET", "/project/info")
        return result
    
    async def search_in_files(self, pattern: str, path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recherche un motif dans les fichiers"""
        endpoint = "/project/search"
        data = {"pattern": pattern}
        if path:
            data["path"] = path
        result = await self._make_request("POST", endpoint, data)
        return result.get("results", [])
    
    # Méthodes utilitaires
    
    async def check_connection(self) -> bool:
        """Vérifie la connexion avec l'API Antigravity"""
        try:
            await self._make_request("GET", "/health")
            return True
        except AntigravityAPIError:
            return False
    
    async def backup_project(self) -> bool:
        """Crée une sauvegarde du projet"""
        result = await self._make_request("POST", "/project/backup")
        return result.get("success", False)
