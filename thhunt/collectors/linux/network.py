import os
from ..base import CollectorBase
from ...utils.logger import setup_logger

logger = setup_logger(__name__)

class LinuxNetworkCollector(CollectorBase):
    def collect(self):
        """
        Collects network connection information from /proc/net/tcp.
        """
        try:
            with open('/proc/net/tcp', 'r') as f:
                lines = f.readlines()
                
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) < 10:
                    continue
                    
                # Parse local and remote addresses
                local_addr_hex, local_port_hex = parts[1].split(':')
                remote_addr_hex, remote_port_hex = parts[2].split(':')
                state = parts[3]
                inode = parts[9]
                
                # Convert hex to IP/Port
                local_ip = self._hex_to_ip(local_addr_hex)
                local_port = int(local_port_hex, 16)
                remote_ip = self._hex_to_ip(remote_addr_hex)
                remote_port = int(remote_port_hex, 16)
                
                # Find PID from inode (simplified, would need to walk /proc/[pid]/fd/)
                pid = self._find_pid_by_inode(inode)

                payload = {
                    "local_ip": local_ip,
                    "local_port": local_port,
                    "remote_ip": remote_ip,
                    "remote_port": remote_port,
                    "state": state,
                    "pid": pid,
                    "inode": inode
                }
                self.publish_event("network_connection", payload)

        except Exception as e:
            logger.error(f"Error in LinuxNetworkCollector: {e}")

    def _hex_to_ip(self, hex_ip):
        # Little-endian for Linux
        try:
            return ".".join(str(int(hex_ip[i:i+2], 16)) for i in range(6, -2, -2))
        except:
            return hex_ip

    def _find_pid_by_inode(self, inode):
        # Placeholder: Real implementation would walk /proc
        return None
