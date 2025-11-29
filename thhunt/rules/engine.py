from typing import List, Dict, Any
import yaml
import os
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class RuleEngine:
    def __init__(self, rules_path: str):
        self.rules_path = rules_path
        self.rules = []
        self.load_rules()

    def load_rules(self):
        """
        Load rules from YAML files.
        """
        if not os.path.exists(self.rules_path):
            logger.warning(f"Rules directory not found: {self.rules_path}")
            return

        for filename in os.listdir(self.rules_path):
            if filename.endswith(".yml") or filename.endswith(".yaml"):
                try:
                    with open(os.path.join(self.rules_path, filename), 'r') as f:
                        rule = yaml.safe_load(f)
                        self.rules.append(rule)
                except Exception as e:
                    logger.error(f"Failed to load rule {filename}: {e}")
        
        logger.info(f"Loaded {len(self.rules)} rules")

    def evaluate(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate event against loaded rules.
        Returns a list of matches (alerts).
        """
        matches = []
        for rule in self.rules:
            if self._match(rule, event):
                matches.append({
                    "rule_name": rule.get("name"),
                    "severity": rule.get("severity"),
                    "description": rule.get("description"),
                    "event": event
                })
        return matches

    def _match(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        conditions = rule.get("conditions", {})
        
        # Check category first
        if "category" in conditions and event.get("category") != conditions["category"]:
            return False

        # Helper to get nested value
        def get_value(obj, path):
            parts = path.split('.')
            for part in parts:
                if isinstance(obj, dict):
                    obj = obj.get(part)
                else:
                    return None
            return obj

        # Process specific conditions
        if conditions.get("category") == "process":
            proc = event.get("process", {})
            
            if "process_name" in conditions:
                if proc.get("name") != conditions["process_name"]:
                    return False
            
            if "process_path_contains" in conditions:
                path = proc.get("path", "")
                if not path or conditions["process_path_contains"].lower() not in path.lower():
                    return False

        return True
