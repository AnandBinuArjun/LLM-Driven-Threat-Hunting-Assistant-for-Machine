from typing import Dict, Any
import platform

def normalize_file_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a file event into a standard schema.
    """
    normalized = {
        "category": "file",
        "timestamp": raw_event.get("timestamp"),
        "host_id": raw_event.get("host_id", "unknown"),
        "os": platform.system().lower(),
        "event_type": raw_event.get("type"),
    }

    payload = raw_event.get("payload", {})
    
    file_data = {
        "path": payload.get("path"),
        "action": payload.get("action"), # created, modified, deleted
        "is_directory": payload.get("is_directory", False),
        "hash": payload.get("hash"), # SHA256 if available
        "size": payload.get("size"),
        "owner": payload.get("owner"),
        "group": payload.get("group"),
        "permissions": payload.get("permissions")
    }
    
    normalized["file"] = file_data
    
    return normalized
