from typing import Dict, Any, List
import json
import time
from ..rules.engine import RuleEngine
from ..baselines.process_baseline import ProcessBaseline
from ..baselines.network_baseline import NetworkBaseline
from ..storage.db import DatabaseManager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class DetectionPipeline:
    def __init__(self, db_path: str, rules_path: str):
        self.db = DatabaseManager(db_path)
        self.rule_engine = RuleEngine(rules_path)
        self.process_baseline = ProcessBaseline(db_path)
        self.network_baseline = NetworkBaseline(db_path)

    def process(self, event: Dict[str, Any]):
        """
        Main entry point for the detection pipeline.
        1. Update Baselines
        2. Check Anomalies
        3. Evaluate Rules
        4. Create Alerts
        """
        # 1. Update Baselines & Check Anomalies
        anomalies = self._check_anomalies(event)
        
        # 2. Evaluate Rules
        rule_matches = self.rule_engine.evaluate(event)
        
        # 3. Create Alerts if any matches or significant anomalies
        if rule_matches or anomalies:
            self._create_alert(event, rule_matches, anomalies)

    def _check_anomalies(self, event: Dict[str, Any]) -> List[str]:
        anomalies = []
        category = event.get("category")
        
        if category == "process":
            path = event.get("process", {}).get("path")
            if self.process_baseline.is_new(path):
                anomalies.append(f"New process seen: {path}")
            self.process_baseline.update(path)
            
        elif category == "network":
            remote_ip = event.get("network", {}).get("remote_ip")
            if self.network_baseline.is_new(remote_ip):
                anomalies.append(f"New remote IP contacted: {remote_ip}")
            self.network_baseline.update(remote_ip)
            
        return anomalies

    def _create_alert(self, event: Dict[str, Any], rule_matches: List[Dict[str, Any]], anomalies: List[str]):
        """
        Constructs and stores an alert.
        """
        # Calculate severity (simple logic for now)
        base_severity = 0
        descriptions = []
        
        for match in rule_matches:
            base_severity = max(base_severity, match.get("severity", 0))
            descriptions.append(f"Rule: {match.get('rule_name')}")
            
        if anomalies:
            base_severity = max(base_severity, 3) # Anomalies have base severity
            descriptions.append(f"Anomalies: {', '.join(anomalies)}")

        alert = {
            "timestamp": time.time(),
            "severity": str(base_severity),
            "rule_name": " | ".join([m.get("rule_name") for m in rule_matches]) if rule_matches else "Anomaly",
            "description": "; ".join(descriptions),
            "related_events": json.dumps([event]), # Store list of events
            "is_enriched": False
        }
        
        # Store alert
        self.db.insert_alert(alert)
        logger.info(f"Generated Alert: {alert['description']}")
