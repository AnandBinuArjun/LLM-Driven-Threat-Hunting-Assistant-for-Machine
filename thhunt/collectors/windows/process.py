import subprocess
import json
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class WindowsProcessCollector(CollectorBase):
    def collect(self):
        """
        Collects process information using PowerShell.
        """
        try:
            # PowerShell command to get process details as JSON
            cmd = [
                "powershell", "-NoProfile", "-Command",
                "Get-Process | Select-Object Id, ProcessName, Path, StartTime, TotalProcessorTime, UserProcessorTime | ConvertTo-Json -Depth 1"
            ]
            
            # Run command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                return

            processes = json.loads(result.stdout)
            
            # Handle single object vs list
            if isinstance(processes, dict):
                processes = [processes]

            for proc in processes:
                # Normalize somewhat
                payload = {
                    "pid": proc.get("Id"),
                    "name": proc.get("ProcessName"),
                    "path": proc.get("Path"),
                    "start_time": str(proc.get("StartTime")), # JSON serialization might need string
                }
                self.publish_event("process_snapshot", payload)

        except subprocess.CalledProcessError as e:
            logger.error(f"PowerShell command failed: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse PowerShell output: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in WindowsProcessCollector: {e}")
