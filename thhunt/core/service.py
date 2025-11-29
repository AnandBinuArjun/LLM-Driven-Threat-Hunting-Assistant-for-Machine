import time
import queue
import threading
import platform
import signal
import sys
from ..config.loader import load_config
from ..storage.db import DatabaseManager
from ..utils.logger import setup_logger
from ..api.server import APIServer
from ..detection.pipeline import DetectionPipeline
from ..enrichment.worker import EnrichmentWorker
from ..normalization.normalize_process import normalize_process_event

logger = setup_logger(__name__)

class ThreatHuntService:
    def __init__(self):
        self.config = load_config()
        self.db = DatabaseManager(self.config.database.path)
        self.event_queue = queue.Queue()
        self.collectors = []
        self.api_server = APIServer(self.config.api, self.config.database.path)
        self.detection_pipeline = DetectionPipeline(self.config.database.path, self.config.detection.rules_path)
        self.enrichment_worker = EnrichmentWorker(self.config.database.path, self.config.llm)
        self.running = False

    def _init_collectors(self):
        os_type = platform.system().lower()
        logger.info(f"Initializing collectors for {os_type}")
        
        if os_type == 'windows':
            try:
                from ..collectors.windows import WindowsProcessCollector, WindowsNetworkCollector
                self.collectors.append(WindowsProcessCollector(self.event_queue, interval=self.config.collectors.process_interval_seconds))
                self.collectors.append(WindowsNetworkCollector(self.event_queue, interval=self.config.collectors.network_interval_seconds))
            except ImportError as e:
                logger.error(f"Failed to import Windows collectors: {e}")
        elif os_type == 'linux':
            try:
                from ..collectors.linux import LinuxProcessCollector, LinuxNetworkCollector
                self.collectors.append(LinuxProcessCollector(self.event_queue, interval=self.config.collectors.process_interval_seconds))
                self.collectors.append(LinuxNetworkCollector(self.event_queue, interval=self.config.collectors.network_interval_seconds))
            except ImportError as e:
                logger.error(f"Failed to import Linux collectors: {e}")
        elif os_type == 'darwin': # macOS
            try:
                from ..collectors.macos import MacOSProcessCollector, MacOSNetworkCollector
                self.collectors.append(MacOSProcessCollector(self.event_queue, interval=self.config.collectors.process_interval_seconds))
                self.collectors.append(MacOSNetworkCollector(self.event_queue, interval=self.config.collectors.network_interval_seconds))
            except ImportError as e:
                logger.error(f"Failed to import macOS collectors: {e}")

    def _process_events(self):
        """
        Main loop to process events from the queue.
        """
        logger.info("Event processor started")
        from ..normalization.normalize_network import normalize_network_event
        from ..normalization.normalize_process import normalize_process_event
        from ..normalization.normalize_file import normalize_file_event
        from ..normalization.normalize_persistence import normalize_persistence_event
        from ..normalization.normalize_auth import normalize_auth_event
        
        while self.running:
            try:
                event = self.event_queue.get(timeout=1)
                
                # 1. Normalize
                normalized_event = event
                event_type = event.get("type")
                
                if event_type == "process_snapshot":
                    normalized_event = normalize_process_event(event)
                elif event_type == "network_connection":
                    normalized_event = normalize_network_event(event)
                elif event_type == "file_change":
                    normalized_event = normalize_file_event(event)
                elif event_type == "persistence_change":
                    normalized_event = normalize_persistence_event(event)
                elif event_type == "auth_event":
                    normalized_event = normalize_auth_event(event)

                # 2. Store in DB
                self.db.insert_event(normalized_event)
                
                # 3. Pass to Detection Engine
                self.detection_pipeline.process(normalized_event)
                
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")

    def start(self):
        self.running = True
        self._init_collectors()
        
        # Start collectors
        for collector in self.collectors:
            collector.start()

        # Start event processor
        self.processor_thread = threading.Thread(target=self._process_events)
        self.processor_thread.daemon = True
        self.processor_thread.start()

        # Start Enrichment Worker
        self.enrichment_worker.start()

        # Start API Server
        self.api_server.start()

        logger.info("Service started successfully")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("Stopping service...")
        self.running = False
        for collector in self.collectors:
            collector.stop()
        self.enrichment_worker.stop()
        # API server is daemon, will stop on exit
        logger.info("Service stopped")

if __name__ == "__main__":
    service = ThreatHuntService()
    service.start()
