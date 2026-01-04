"""
Mode Auto-Accept pour automatiser les actions des agents
"""
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
from loguru import logger
import asyncio


class ActionType(Enum):
    """Types d'actions qui peuvent être acceptées automatiquement"""
    FILE_WRITE = "file_write"
    TERMINAL_COMMAND = "terminal_command"
    CODE_GENERATION = "code_generation"
    TEST_EXECUTION = "test_execution"
    CODE_REVIEW = "code_review"


@dataclass
class AutoAcceptRule:
    """Règle pour l'acceptation automatique"""
    action_type: ActionType
    enabled: bool = True
    requires_confirmation: bool = False
    max_file_size_mb: int = 10
    allowed_patterns: List[str] = None
    blocked_patterns: List[str] = None
    custom_validator: Optional[Callable] = None
    
    def __post_init__(self):
        if self.allowed_patterns is None:
            self.allowed_patterns = []
        if self.blocked_patterns is None:
            self.blocked_patterns = []


class AutoAcceptManager:
    """Gestionnaire du mode Auto-Accept"""
    
    def __init__(self):
        self.enabled = False
        self.rules: Dict[ActionType, AutoAcceptRule] = {}
        
        # Statistiques
        self.actions_processed = 0
        self.actions_auto_accepted = 0
        self.actions_rejected = 0
        self.actions_required_confirmation = 0
        
        # Historique des actions
        self.action_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Initialiser les règles par défaut
        self._init_default_rules()
        
        logger.info("AutoAcceptManager initialisé")
    
    def _init_default_rules(self):
        """Initialise les règles par défaut"""
        self.rules[ActionType.FILE_WRITE] = AutoAcceptRule(
            action_type=ActionType.FILE_WRITE,
            enabled=True,
            max_file_size_mb=10,
            blocked_patterns=["*.env", "*.key", "*secret*"]
        )
        
        self.rules[ActionType.TERMINAL_COMMAND] = AutoAcceptRule(
            action_type=ActionType.TERMINAL_COMMAND,
            enabled=True,  # Activé par défaut (contrôlé par le switch global)
            requires_confirmation=False, # Vrai auto-accept
            blocked_patterns=["rm -rf", "del /S /Q", "format", "mkfs", "sudo", "Format-Volume"]
        )
        
        self.rules[ActionType.CODE_GENERATION] = AutoAcceptRule(
            action_type=ActionType.CODE_GENERATION,
            enabled=True,
            max_file_size_mb=5
        )
        
        self.rules[ActionType.TEST_EXECUTION] = AutoAcceptRule(
            action_type=ActionType.TEST_EXECUTION,
            enabled=True
        )
        
        self.rules[ActionType.CODE_REVIEW] = AutoAcceptRule(
            action_type=ActionType.CODE_REVIEW,
            enabled=True
        )
    
    def toggle(self) -> bool:
        """Active/désactive le mode Auto-Accept"""
        self.enabled = not self.enabled
        logger.info(f"Mode Auto-Accept: {'activé' if self.enabled else 'désactivé'}")
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        """Définit l'état du mode Auto-Accept"""
        self.enabled = enabled
        logger.info(f"Mode Auto-Accept: {'activé' if self.enabled else 'désactivé'}")
    
    def update_rule(self, action_type: ActionType, rule: AutoAcceptRule):
        """Met à jour une règle"""
        self.rules[action_type] = rule
        logger.info(f"Règle mise à jour pour {action_type.value}")
    
    def enable_rule(self, action_type: ActionType):
        """Active une règle spécifique"""
        if action_type in self.rules:
            self.rules[action_type].enabled = True
            logger.info(f"Règle activée pour {action_type.value}")
    
    def disable_rule(self, action_type: ActionType):
        """Désactive une règle spécifique"""
        if action_type in self.rules:
            self.rules[action_type].enabled = False
            logger.info(f"Règle désactivée pour {action_type.value}")
    
    async def should_accept_action(
        self,
        action_type: ActionType,
        action_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Détermine si une action doit être acceptée automatiquement
        
        Retourne un dictionnaire avec:
        - accept: bool - si l'action doit être acceptée
        - requires_confirmation: bool - si une confirmation est nécessaire
        - reason: str - raison de la décision
        """
        self.actions_processed += 1
        
        result = {
            "accept": False,
            "requires_confirmation": False,
            "reason": ""
        }
        
        # Vérifier si le mode Auto-Accept est activé
        if not self.enabled:
            result["reason"] = "Auto-Accept désactivé"
            self._log_action(action_type, action_data, result)
            return result
        
        # Récupérer la règle pour ce type d'action
        rule = self.rules.get(action_type)
        if not rule:
            result["reason"] = f"Aucune règle pour {action_type.value}"
            self._log_action(action_type, action_data, result)
            return result
        
        # Vérifier si la règle est activée
        if not rule.enabled:
            result["reason"] = f"Règle désactivée pour {action_type.value}"
            self._log_action(action_type, action_data, result)
            return result
        
        # Vérifier si une confirmation est requise
        if rule.requires_confirmation:
            result["requires_confirmation"] = True
            result["reason"] = "Confirmation requise par la règle"
            self.actions_required_confirmation += 1
            self._log_action(action_type, action_data, result)
            return result
        
        # Valider avec le validateur personnalisé si fourni
        if rule.custom_validator:
            try:
                custom_result = await rule.custom_validator(action_data)
                if not custom_result["accept"]:
                    result["reason"] = custom_result.get("reason", "Rejeté par le validateur personnalisé")
                    self._log_action(action_type, action_data, result)
                    return result
            except Exception as e:
                logger.error(f"Erreur dans le validateur personnalisé: {e}")
                result["reason"] = f"Erreur dans le validateur: {e}"
                self._log_action(action_type, action_data, result)
                return result
        
        # Vérifier les motifs bloqués
        if self._is_blocked(action_data, rule.blocked_patterns):
            result["reason"] = "Action bloquée par un motif"
            self.actions_rejected += 1
            self._log_action(action_type, action_data, result)
            return result
        
        # Vérifier les motifs autorisés
        if rule.allowed_patterns and not self._is_allowed(action_data, rule.allowed_patterns):
            result["reason"] = "Action non autorisée par les motifs"
            self.actions_rejected += 1
            self._log_action(action_type, action_data, result)
            return result
        
        # Vérifier la taille du fichier (si applicable)
        if action_type == ActionType.FILE_WRITE:
            file_size = action_data.get("file_size", 0)
            max_size = rule.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                result["reason"] = f"Fichier trop volumineux ({file_size} > {max_size} octets)"
                self.actions_rejected += 1
                self._log_action(action_type, action_data, result)
                return result
        
        # Si tout est OK, accepter l'action
        result["accept"] = True
        result["reason"] = "Action acceptée automatiquement"
        self.actions_auto_accepted += 1
        self._log_action(action_type, action_data, result)
        
        return result
    
    def _is_blocked(self, action_data: Dict[str, Any], blocked_patterns: List[str]) -> bool:
        """Vérifie si l'action correspond à un motif bloqué"""
        import fnmatch
        
        for pattern in blocked_patterns:
            # Vérifier dans le contenu
            content = str(action_data)
            if fnmatch.fnmatch(content.lower(), pattern.lower()):
                return True
            
            # Vérifier dans les fichiers spécifiques
            file_path = action_data.get("file_path", "")
            if fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                return True
        
        return False
    
    def _is_allowed(self, action_data: Dict[str, Any], allowed_patterns: List[str]) -> bool:
        """Vérifie si l'action correspond à un motif autorisé"""
        import fnmatch
        
        for pattern in allowed_patterns:
            # Vérifier dans le contenu
            content = str(action_data)
            if fnmatch.fnmatch(content.lower(), pattern.lower()):
                return True
            
            # Vérifier dans les fichiers spécifiques
            file_path = action_data.get("file_path", "")
            if fnmatch.fnmatch(file_path.lower(), pattern.lower()):
                return True
        
        return False
    
    def _log_action(self, action_type: ActionType, action_data: Dict[str, Any], result: Dict[str, Any]):
        """Journalise une action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type.value,
            "data": action_data,
            "result": result
        }
        
        self.action_history.append(log_entry)
        
        # Limiter la taille de l'historique
        if len(self.action_history) > self.max_history_size:
            self.action_history = self.action_history[-self.max_history_size:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques"""
        return {
            "enabled": self.enabled,
            "actions_processed": self.actions_processed,
            "actions_auto_accepted": self.actions_auto_accepted,
            "actions_rejected": self.actions_rejected,
            "actions_required_confirmation": self.actions_required_confirmation,
            "auto_accept_rate": (
                self.actions_auto_accepted / self.actions_processed * 100
                if self.actions_processed > 0
                else 0
            ),
            "rules": {
                action_type.value: {
                    "enabled": rule.enabled,
                    "requires_confirmation": rule.requires_confirmation
                }
                for action_type, rule in self.rules.items()
            }
        }
    
    def get_recent_actions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retourne les actions récentes"""
        return self.action_history[-limit:]
    
    def clear_history(self):
        """Efface l'historique des actions"""
        self.action_history.clear()
        logger.info("Historique des actions effacé")
    
    def reset_statistics(self):
        """Réinitialise les statistiques"""
        self.actions_processed = 0
        self.actions_auto_accepted = 0
        self.actions_rejected = 0
        self.actions_required_confirmation = 0
        logger.info("Statistiques réinitialisées")
