"""
Gestionnaire de cache pour les tâches et conversations
"""
from typing import Dict, List, Optional, Any
from pathlib import Path
import shutil
import json
from datetime import datetime
from dataclasses import dataclass, field
from loguru import logger

from .dashboard import CacheEntry


@dataclass
class CacheConfig:
    """Configuration du cache"""
    auto_clean_enabled: bool = False
    auto_clean_threshold_mb: int = 500  # MB
    auto_clean_keep_count: int = 5
    max_age_days: int = 30
    warning_threshold_mb: int = 500
    check_interval_seconds: int = 120


class CacheManager:
    """Gestionnaire de cache pour les tâches et conversations"""
    
    def __init__(self, cache_dir: Path, config: Optional[CacheConfig] = None):
        self.cache_dir = cache_dir
        self.config = config or CacheConfig()
        
        # Créer le répertoire de cache
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Index des entrées de cache
        self.cache_index: Dict[str, CacheEntry] = {}
        
        # Initialiser l'index
        self._load_index()
        
        logger.info(f"CacheManager initialisé: {self.cache_dir}")
    
    def _load_index(self):
        """Charge l'index depuis le fichier"""
        index_file = self.cache_dir / "cache_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for task_id, entry_data in data.items():
                    self.cache_index[task_id] = CacheEntry(
                        task_id=task_id,
                        agent_type=entry_data.get("agent_type", ""),
                        file_count=entry_data.get("file_count", 0),
                        total_size=entry_data.get("total_size", 0),
                        created_at=datetime.fromisoformat(entry_data.get("created_at", datetime.now().isoformat())),
                        preview=entry_data.get("preview")
                    )
                
                logger.info(f"Index de cache chargé: {len(self.cache_index)} entrées")
            except Exception as e:
                logger.error(f"Erreur lors du chargement de l'index: {e}")
    
    def _save_index(self):
        """Sauvegarde l'index dans le fichier"""
        index_file = self.cache_dir / "cache_index.json"
        
        try:
            data = {}
            for task_id, entry in self.cache_index.items():
                data[task_id] = {
                    "agent_type": entry.agent_type,
                    "file_count": entry.file_count,
                    "total_size": entry.total_size,
                    "created_at": entry.created_at.isoformat(),
                    "preview": entry.preview
                }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Index sauvegardé: {len(self.cache_index)} entrées")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'index: {e}")
    
    def create_cache_entry(
        self,
        task_id: str,
        agent_type: str,
        files: Dict[str, Any] = None,
        preview: Optional[str] = None
    ) -> Path:
        """Crée une nouvelle entrée de cache"""
        task_dir = self.cache_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculer la taille et le nombre de fichiers
        total_size = 0
        file_count = 0
        
        if files:
            for file_name, content in files.items():
                file_path = task_dir / file_name
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                if isinstance(content, str):
                    content_bytes = content.encode('utf-8')
                else:
                    content_bytes = content
                
                with open(file_path, 'wb') as f:
                    f.write(content_bytes)
                
                total_size += len(content_bytes)
                file_count += 1
        
        # Créer l'entrée dans l'index
        self.cache_index[task_id] = CacheEntry(
            task_id=task_id,
            agent_type=agent_type,
            file_count=file_count,
            total_size=total_size,
            preview=preview
        )
        
        self._save_index()
        logger.info(f"Entrée de cache créée: {task_id} ({total_size / 1024 / 1024:.2f} MB, {file_count} fichiers)")
        
        return task_dir
    
    def get_cache_entry(self, task_id: str) -> Optional[CacheEntry]:
        """Récupère une entrée de cache"""
        return self.cache_index.get(task_id)
    
    def list_cache_entries(self, agent_type: Optional[str] = None) -> List[CacheEntry]:
        """Liste les entrées de cache, optionnellement filtrées par type d'agent"""
        entries = list(self.cache_index.values())
        
        if agent_type:
            entries = [e for e in entries if e.agent_type == agent_type]
        
        # Trier par date de création (plus récent d'abord)
        entries.sort(key=lambda e: e.created_at, reverse=True)
        
        return entries
    
    def delete_cache_entry(self, task_id: str) -> bool:
        """Supprime une entrée de cache"""
        if task_id not in self.cache_index:
            return False
        
        task_dir = self.cache_dir / task_id
        
        try:
            # Supprimer le répertoire
            if task_dir.exists():
                shutil.rmtree(task_dir)
            
            # Supprimer de l'index
            del self.cache_index[task_id]
            self._save_index()
            
            logger.info(f"Entrée de cache supprimée: {task_id}")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {task_id}: {e}")
            return False
    
    def clear_all_cache(self) -> int:
        """Supprime tout le cache et retourne le nombre d'entrées supprimées"""
        count = len(self.cache_index)
        
        for task_id in list(self.cache_index.keys()):
            self.delete_cache_entry(task_id)
        
        logger.info(f"{count} entrées de cache supprimées")
        return count
    
    def get_total_size(self) -> int:
        """Retourne la taille totale du cache en octets"""
        return sum(entry.total_size for entry in self.cache_index.values())
    
    def get_size_by_agent_type(self) -> Dict[str, int]:
        """Retourne la taille du cache par type d'agent"""
        sizes = {}
        for entry in self.cache_index.values():
            if entry.agent_type not in sizes:
                sizes[entry.agent_type] = 0
            sizes[entry.agent_type] += entry.total_size
        return sizes
    
    def auto_clean(self) -> int:
        """Nettoie automatiquement le cache si nécessaire"""
        if not self.config.auto_clean_enabled:
            return 0
        
        total_size_mb = self.get_total_size() / (1024 * 1024)
        
        if total_size_mb < self.config.auto_clean_threshold_mb:
            logger.debug(f"Cache size ({total_size_mb:.2f} MB) sous le seuil, pas de nettoyage")
            return 0
        
        logger.info(f"Auto-clean activé: {total_size_mb:.2f} MB > {self.config.auto_clean_threshold_mb} MB")
        
        # Trier par âge (plus ancien en premier)
        entries = sorted(
            self.cache_index.values(),
            key=lambda e: e.created_at
        )
        
        # Conserver les N plus récentes
        to_delete = entries[:-self.config.auto_clean_keep_count]
        
        deleted_count = 0
        for entry in to_delete:
            if self.delete_cache_entry(entry.task_id):
                deleted_count += 1
        
        new_size_mb = self.get_total_size() / (1024 * 1024)
        logger.info(f"Auto-clean terminé: {deleted_count} entrées supprimées, {new_size_mb:.2f} MB restant")
        
        return deleted_count
    
    def cleanup_old_entries(self, max_age_days: Optional[int] = None) -> int:
        """Supprime les entrées plus vieilles qu'un certain nombre de jours"""
        max_age = max_age_days or self.config.max_age_days
        cutoff_date = datetime.now() - timedelta(days=max_age)
        
        to_delete = [
            task_id
            for task_id, entry in self.cache_index.items()
            if entry.created_at < cutoff_date
        ]
        
        deleted_count = 0
        for task_id in to_delete:
            if self.delete_cache_entry(task_id):
                deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"{deleted_count} entrées anciennes supprimées (> {max_age} jours)")
        
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        total_size = self.get_total_size()
        entries = list(self.cache_index.values())
        
        # Calculer les âges
        from datetime import timedelta
        now = datetime.now()
        ages = [(now - e.created_at).total_seconds() for e in entries]
        avg_age = sum(ages) / len(ages) if ages else 0
        
        return {
            "total_entries": len(entries),
            "total_size_mb": total_size / (1024 * 1024),
            "total_files": sum(e.file_count for e in entries),
            "by_agent_type": {
                agent_type: size / (1024 * 1024)
                for agent_type, size in self.get_size_by_agent_type().items()
            },
            "oldest_entry": min(entries, key=lambda e: e.created_at).created_at.isoformat() if entries else None,
            "newest_entry": max(entries, key=lambda e: e.created_at).created_at.isoformat() if entries else None,
            "avg_age_hours": avg_age / 3600 if ages else 0
        }
    
    def preview_cache_entry(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Prévisualise le contenu d'une entrée de cache"""
        if task_id not in self.cache_index:
            return None
        
        entry = self.cache_index[task_id]
        task_dir = self.cache_dir / task_id
        
        if not task_dir.exists():
            return None
        
        # Lister les fichiers
        files_info = []
        for file_path in task_dir.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(task_dir)
                files_info.append({
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "size_mb": file_path.stat().st_size / (1024 * 1024)
                })
        
        return {
            "task_id": task_id,
            "agent_type": entry.agent_type,
            "file_count": entry.file_count,
            "total_size_mb": entry.total_size / (1024 * 1024),
            "created_at": entry.created_at.isoformat(),
            "files": files_info
        }
