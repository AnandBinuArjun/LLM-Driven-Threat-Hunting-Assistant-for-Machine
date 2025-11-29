import unittest
from thhunt.normalization.normalize_process import normalize_process_event

class TestNormalization(unittest.TestCase):
    def test_normalize_process_event(self):
        raw_event = {
            "type": "process_snapshot",
            "timestamp": 1234567890.0,
            "host_id": "test-host",
            "payload": {
                "pid": 1234,
                "ppid": 1,
                "name": "test_proc",
                "path": "/bin/test_proc",
                "cmdline": "test_proc --arg",
                "user": "root",
                "start_time": "2023-01-01T00:00:00"
            }
        }

        normalized = normalize_process_event(raw_event)

        self.assertEqual(normalized["category"], "process")
        self.assertEqual(normalized["timestamp"], 1234567890.0)
        self.assertEqual(normalized["process"]["pid"], 1234)
        self.assertEqual(normalized["process"]["name"], "test_proc")
        self.assertEqual(normalized["process"]["path"], "/bin/test_proc")

    def test_normalize_empty_payload(self):
        raw_event = {
            "type": "process_snapshot",
            "timestamp": 1234567890.0,
            "payload": {}
        }
        normalized = normalize_process_event(raw_event)
        self.assertEqual(normalized["category"], "process")
        self.assertIsNone(normalized["process"]["pid"])

if __name__ == '__main__':
    unittest.main()
