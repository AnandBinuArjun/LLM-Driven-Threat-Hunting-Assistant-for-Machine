import unittest
from thhunt.normalization.normalize_network import normalize_network_event

class TestNetworkNormalization(unittest.TestCase):
    def test_normalize_network_event(self):
        raw_event = {
            "type": "network_connection",
            "timestamp": 1234567890.0,
            "host_id": "test-host",
            "payload": {
                "local_ip": "192.168.1.10",
                "local_port": 12345,
                "remote_ip": "8.8.8.8",
                "remote_port": 53,
                "state": "ESTABLISHED",
                "pid": 100,
                "protocol": "tcp"
            }
        }

        normalized = normalize_network_event(raw_event)

        self.assertEqual(normalized["category"], "network")
        self.assertEqual(normalized["network"]["remote_ip"], "8.8.8.8")
        self.assertEqual(normalized["network"]["remote_port"], 53)
        self.assertEqual(normalized["network"]["pid"], 100)

if __name__ == '__main__':
    unittest.main()
