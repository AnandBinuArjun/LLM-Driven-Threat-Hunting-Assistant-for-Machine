from typing import Dict, Any
import platform

def normalize_network_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes a network event into a standard schema.
    """
    normalized = {
        "category": "network",
        "timestamp": raw_event.get("timestamp"),
        "host_id": raw_event.get("host_id", "unknown"),
        "os": platform.system().lower(),
        "event_type": raw_event.get("type"),
    }

    payload = raw_event.get("payload", {})
    
    network_data = {
        "local_ip": payload.get("local_ip"),
        "local_port": payload.get("local_port"),
        "remote_ip": payload.get("remote_ip"),
        "remote_port": payload.get("remote_port"),
        "protocol": payload.get("protocol", "tcp"), # Default to tcp for now
        "state": payload.get("state"),
        "pid": payload.get("pid"),
        "process_name": payload.get("process_name") # If available
    }
    
    normalized["network"] = network_data
    
    return normalized
