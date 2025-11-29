import os
import yaml
import platform
import uuid
from .schema import Config, DatabaseConfig, LLMConfig, CollectorConfig, DetectionConfig, APIConfig

def load_config(config_path: str = "config.yaml") -> Config:
    """
    Loads configuration from a YAML file or returns defaults.
    """
    
    # Default values
    os_type = platform.system().lower()
    host_id = str(uuid.uuid4())
    
    config_data = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Error loading config file: {e}")

    # Helper to load nested configs
    def load_section(section_class, section_name):
        return section_class(**config_data.get(section_name, {}))

    return Config(
        os_type=config_data.get('os_type', os_type),
        host_id=config_data.get('host_id', host_id),
        database=load_section(DatabaseConfig, 'database'),
        llm=load_section(LLMConfig, 'llm'),
        collectors=load_section(CollectorConfig, 'collectors'),
        detection=load_section(DetectionConfig, 'detection'),
        api=load_section(APIConfig, 'api')
    )
