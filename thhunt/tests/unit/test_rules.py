import unittest
import os
import tempfile
import shutil
from thhunt.rules.engine import RuleEngine

class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.rules_path = os.path.join(self.test_dir, "rules")
        os.makedirs(self.rules_path)
        
        # Create a dummy rule
        with open(os.path.join(self.rules_path, "test_rule.yml"), "w") as f:
            f.write("""
name: Test Rule
description: Detects test process
severity: 5
conditions:
  category: process
  process_name: "malware.exe"
""")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_rule_match(self):
        engine = RuleEngine(self.rules_path)
        
        event_match = {
            "category": "process",
            "process": {
                "name": "malware.exe",
                "path": "/tmp/malware.exe"
            }
        }
        
        matches = engine.evaluate(event_match)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["rule_name"], "Test Rule")

    def test_rule_no_match(self):
        engine = RuleEngine(self.rules_path)
        
        event_no_match = {
            "category": "process",
            "process": {
                "name": "benign.exe",
                "path": "/bin/benign.exe"
            }
        }
        
        matches = engine.evaluate(event_no_match)
        self.assertEqual(len(matches), 0)

if __name__ == '__main__':
    unittest.main()
