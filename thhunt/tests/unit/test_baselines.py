import unittest
import os
import tempfile
import shutil
from thhunt.baselines.process_baseline import ProcessBaseline

class TestProcessBaseline(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test.db")
        self.baseline = ProcessBaseline(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_new_process(self):
        path = "/bin/new_proc"
        self.assertTrue(self.baseline.is_new(path))
        
        self.baseline.update(path)
        self.assertFalse(self.baseline.is_new(path))

    def test_update_count(self):
        path = "/bin/proc"
        self.baseline.update(path)
        self.baseline.update(path)
        
        conn = self.baseline._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM baseline_process WHERE path = ?", (path,))
        row = cursor.fetchone()
        conn.close()
        
        self.assertEqual(row[0], 2)

if __name__ == '__main__':
    unittest.main()
