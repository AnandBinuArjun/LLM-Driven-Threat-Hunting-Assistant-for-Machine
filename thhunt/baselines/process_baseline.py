import sqlite3
import time
from typing import Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ProcessBaseline:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baseline_process (
                path TEXT PRIMARY KEY,
                first_seen REAL,
                last_seen REAL,
                count INTEGER DEFAULT 1,
                is_known_good BOOLEAN DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def update(self, process_path: str):
        """
        Updates the baseline with a seen process path.
        """
        if not process_path:
            return

        conn = self._get_connection()
        cursor = conn.cursor()
        now = time.time()
        
        try:
            cursor.execute('SELECT count FROM baseline_process WHERE path = ?', (process_path,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    UPDATE baseline_process 
                    SET last_seen = ?, count = count + 1 
                    WHERE path = ?
                ''', (now, process_path))
            else:
                cursor.execute('''
                    INSERT INTO baseline_process (path, first_seen, last_seen, count)
                    VALUES (?, ?, ?, 1)
                ''', (process_path, now, now))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating process baseline: {e}")
        finally:
            conn.close()

    def is_new(self, process_path: str) -> bool:
        """
        Checks if a process path is new (not in baseline).
        """
        if not process_path:
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM baseline_process WHERE path = ?', (process_path,))
        row = cursor.fetchone()
        conn.close()
        
        return row is None
