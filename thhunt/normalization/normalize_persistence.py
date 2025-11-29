from typing import Dict, Any
import platform

def normalize_persistence_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a persistence event into a standard schema.
    """
    normalized = {
        "category": "persistence",
        "timestamp": raw_event.get("timestamp"),
        "host_id": raw_event.get("host_id", "unknown"),
        "os": platform.system().lower(),
        "event_type": raw_event.get("type"),
    }

    payload = raw_event.get("payload", {})
    
    persistence_data = {
        "mechanism": payload.get("mechanism"), # e.g., "crontab", "registry_run", "service"
        "entry_name": payload.get("entry_name"),
        "command": payload.get("command"),
        "path": payload.get("path"), # File path associated with the persistence
        "user": payload.get("user")
    }
    
    normalized["persistence"] = persistence_data
    
    return normalized
