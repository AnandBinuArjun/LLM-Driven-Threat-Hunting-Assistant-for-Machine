from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class DatabaseConfig:
    path: str = "thhunt.db"

@dataclass
class LLMConfig:
    provider: str = "ollama"  # ollama, lmstudio, etc.
    base_url: str = "http://localhost:11434"
    model: str = "llama3"
    timeout: int = 30

@dataclass
class CollectorConfig:
    process_interval_seconds: int = 5
    network_interval_seconds: int = 10
    file_watch_paths: List[str] = field(default_factory=list)

@dataclass
class DetectionConfig:
    rules_path: str = "rules/"
    enable_anomaly_detection: bool = True

@dataclass
class APIConfig:
    host: str = "127.0.0.1"
    port: int = 9999

@dataclass
class Config:
    os_type: str
    host_id: str
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    collectors: CollectorConfig = field(default_factory=CollectorConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    api: APIConfig = field(default_factory=APIConfig)
