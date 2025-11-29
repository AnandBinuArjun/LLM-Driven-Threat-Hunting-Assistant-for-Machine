import subprocess
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class MacOSNetworkCollector(CollectorBase):
    def collect(self):
        """
        Collects network connection information using netstat.
        """
        try:
            # netstat -anv -p tcp
            cmd = ["netstat", "-anv", "-p", "tcp"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            # Skip headers (usually 2 lines)
            if len(lines) < 3:
                return

            for line in lines[2:]:
                parts = line.split()
                if len(parts) < 6:
                    continue
                
                # Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)     rhiwat shiwat    pid   epid  state    options
                # tcp4       0      0  127.0.0.1.12345        *.*                    LISTEN      131072 131072    1234      0  0x0000   0x00000000
                
                try:
                    proto = parts[0]
                    local_addr = parts[3]
                    foreign_addr = parts[4]
                    state = parts[5]
                    pid = parts[8] if len(parts) > 8 else None

                    # Parse IP/Port
                    local_ip, local_port = self._parse_addr(local_addr)
                    remote_ip, remote_port = self._parse_addr(foreign_addr)

                    payload = {
                        "local_ip": local_ip,
                        "local_port": local_port,
                        "remote_ip": remote_ip,
                        "remote_port": remote_port,
                        "state": state,
                        "pid": int(pid) if pid and pid.isdigit() else None,
                        "protocol": proto
                    }
                    self.publish_event("network_connection", payload)
                except Exception:
                    continue

        except subprocess.CalledProcessError as e:
            logger.error(f"netstat command failed: {e}")
        except Exception as e:
            logger.error(f"Error in MacOSNetworkCollector: {e}")

    def _parse_addr(self, addr):
        if '.' in addr:
            parts = addr.rsplit('.', 1)
            if len(parts) == 2:
                return parts[0], parts[1]
        return addr, ""
