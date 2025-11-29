from typing import Dict, Any
import platform

def normalize_process_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a process event into a standard schema.
    """
    # Basic envelope
    normalized = {
        "category": "process",
        "timestamp": raw_event.get("timestamp"),
        "host_id": raw_event.get("host_id", "unknown"),
        "os": platform.system().lower(),
        "event_type": raw_event.get("type"),
    }

    payload = raw_event.get("payload", {})
    
    # Process specific fields
    process_data = {
        "pid": payload.get("pid"),
        "ppid": payload.get("ppid"),
        "name": payload.get("name"),
        "path": payload.get("path"),
        "cmdline": payload.get("cmdline"),
        "user": payload.get("user"),
        "hash": payload.get("hash"),
        "start_time": payload.get("start_time"),
    }
    
    normalized["process"] = process_data
    
    return normalized
