import subprocess
import json
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class MacOSProcessCollector(CollectorBase):
    def collect(self):
        """
        Collects process information using ps.
        """
        try:
            # ps -eo pid,ppid,user,comm,command
            cmd = ["ps", "-eo", "pid,ppid,user,comm,command"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            # Skip header
            if len(lines) < 2:
                return

            for line in lines[1:]:
                # Parsing ps output can be tricky due to spaces in commands.
                # This is a simplified parser.
                parts = line.split(maxsplit=4)
                if len(parts) >= 4:
                    try:
                        payload = {
                            "pid": int(parts[0]),
                            "ppid": int(parts[1]),
                            "user": parts[2],
                            "name": parts[3].split('/')[-1], # Simple name from path
                            "path": parts[3],
                            "cmdline": parts[4] if len(parts) > 4 else ""
                        }
                        self.publish_event("process_snapshot", payload)
                    except ValueError:
                        continue

        except subprocess.CalledProcessError as e:
            logger.error(f"ps command failed: {e}")
        except Exception as e:
            logger.error(f"Error in MacOSProcessCollector: {e}")
