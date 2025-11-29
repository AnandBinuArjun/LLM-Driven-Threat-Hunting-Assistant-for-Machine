import os
import time
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class LinuxProcessCollector(CollectorBase):
    def collect(self):
        """
        Collects process information by iterating over /proc.
        """
        try:
            # Iterate over all PIDs in /proc
            pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
            
            for pid in pids:
                try:
                    pid_path = os.path.join('/proc', pid)
                    
                    # Read command line
                    try:
                        with open(os.path.join(pid_path, 'cmdline'), 'r') as f:
                            cmdline = f.read().replace('\0', ' ').strip()
                    except (IOError, OSError):
                        cmdline = ""

                    # Read status for Name, PPID, Uid
                    status = {}
                    try:
                        with open(os.path.join(pid_path, 'status'), 'r') as f:
                            for line in f:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    status[parts[0].strip()] = parts[1].strip()
                    except (IOError, OSError):
                        pass

                    # Read exe link
                    try:
                        exe_path = os.readlink(os.path.join(pid_path, 'exe'))
                    except (IOError, OSError):
                        exe_path = ""

                    # Construct payload
                    if status.get("Name"):
                        payload = {
                            "pid": int(pid),
                            "ppid": int(status.get("PPid", 0)),
                            "name": status.get("Name"),
                            "path": exe_path,
                            "cmdline": cmdline,
                            "user": status.get("Uid", "").split()[0] if status.get("Uid") else "unknown",
                            # "start_time": ... # Could read /proc/uptime and /proc/[pid]/stat to calc start time
                        }
                        self.publish_event("process_snapshot", payload)

                except Exception as e:
                    # Process might have ended while reading
                    continue

        except Exception as e:
            logger.error(f"Error in LinuxProcessCollector: {e}")
