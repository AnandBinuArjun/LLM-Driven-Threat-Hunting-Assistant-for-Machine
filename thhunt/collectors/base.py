from abc import ABC, abstractmethod
import threading
import time
import queue
from typing import Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class CollectorBase(ABC, threading.Thread):
    def __init__(self, event_queue: queue.Queue, interval: int = 5):
        super().__init__()
        self.event_queue = event_queue
        self.interval = interval
        self.running = True
        self.daemon = True # Daemon thread to exit when main program exits

    def run(self):
        logger.info(f"Starting collector: {self.__class__.__name__}")
        while self.running:
            try:
                self.collect()
            except Exception as e:
                logger.error(f"Error in {self.__class__.__name__}: {e}")
            
            time.sleep(self.interval)
        logger.info(f"Stopping collector: {self.__class__.__name__}")

    def stop(self):
        self.running = False

    @abstractmethod
    def collect(self):
        """
        Collect telemetry and put normalized events into self.event_queue
        """
        pass

    def publish_event(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "timestamp": time.time(),
            "collector": self.__class__.__name__,
            "type": event_type,
            "payload": payload
        }
        self.event_queue.put(event)
