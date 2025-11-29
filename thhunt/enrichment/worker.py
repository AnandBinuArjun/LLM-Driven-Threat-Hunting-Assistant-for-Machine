import threading
import time
import json
from ..storage.db import DatabaseManager
from ..llm.client import LLMClient
from ..config.loader import LLMConfig
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class EnrichmentWorker(threading.Thread):
    def __init__(self, db_path: str, llm_config: LLMConfig, interval: int = 10):
        super().__init__()
        self.db = DatabaseManager(db_path)
        self.llm_client = LLMClient(llm_config)
        self.interval = interval
        self.running = True
        self.daemon = True

    def run(self):
        logger.info("Enrichment worker started")
        while self.running:
            try:
                self._process_alerts()
            except Exception as e:
                logger.error(f"Error in enrichment worker: {e}")
            
            time.sleep(self.interval)
        logger.info("Enrichment worker stopped")

    def _process_alerts(self):
        alerts = self.db.get_unenriched_alerts()
        if not alerts:
            return

        logger.info(f"Found {len(alerts)} unenriched alerts")
        for alert in alerts:
            try:
                logger.info(f"Enriching alert {alert['id']}")
                enrichment = self.llm_client.enrich_alert(alert)
                if enrichment:
                    self.db.update_alert_enrichment(alert['id'], enrichment)
                    logger.info(f"Alert {alert['id']} enriched successfully")
            except Exception as e:
                logger.error(f"Failed to enrich alert {alert['id']}: {e}")

    def stop(self):
        self.running = False
