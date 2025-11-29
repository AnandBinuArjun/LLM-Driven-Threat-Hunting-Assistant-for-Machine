from typing import Dict, Any
import platform

def normalize_auth_event(raw_event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizes an authentication event into a standard schema.
    """
    normalized = {
        "category": "auth",
        "timestamp": raw_event.get("timestamp"),
        "host_id": raw_event.get("host_id", "unknown"),
        "os": platform.system().lower(),
        "event_type": raw_event.get("type"),
    }

    payload = raw_event.get("payload", {})
    
    auth_data = {
        "user": payload.get("user"),
        "src_ip": payload.get("src_ip"),
        "result": payload.get("result"), # success, failure
        "method": payload.get("method"), # password, publickey, etc.
        "service": payload.get("service"), # ssh, sudo, login
        "message": payload.get("message")
    }
    
    normalized["auth"] = auth_data
    
    return normalized
