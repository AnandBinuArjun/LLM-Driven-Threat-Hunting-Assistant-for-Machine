import subprocess
import json
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class WindowsNetworkCollector(CollectorBase):
    def collect(self):
        """
        Collects network connection information using PowerShell (Get-NetTCPConnection).
        """
        try:
            # PowerShell command to get TCP connections
            cmd = [
                "powershell", "-NoProfile", "-Command",
                "Get-NetTCPConnection | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort, State, OwningProcess, CreationTime | ConvertTo-Json -Depth 1"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                return

            connections = json.loads(result.stdout)
            
            if isinstance(connections, dict):
                connections = [connections]

            for conn in connections:
                payload = {
                    "local_ip": conn.get("LocalAddress"),
                    "local_port": conn.get("LocalPort"),
                    "remote_ip": conn.get("RemoteAddress"),
                    "remote_port": conn.get("RemotePort"),
                    "state": conn.get("State"),
                    "pid": conn.get("OwningProcess"),
                    "timestamp": str(conn.get("CreationTime"))
                }
                self.publish_event("network_connection", payload)

        except subprocess.CalledProcessError as e:
            logger.error(f"PowerShell command failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PowerShell output: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in WindowsNetworkCollector: {e}")
