import sqlite3
import time
from typing import Dict, Any
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class NetworkBaseline:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baseline_network (
                remote_ip TEXT PRIMARY KEY,
                first_seen REAL,
                last_seen REAL,
                count INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    def update(self, remote_ip: str):
        """
        Updates the baseline with a seen remote IP.
        """
        if not remote_ip or remote_ip in ['127.0.0.1', '::1', '0.0.0.0']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()
        now = time.time()
        
        try:
            cursor.execute('SELECT count FROM baseline_network WHERE remote_ip = ?', (remote_ip,))
            row = cursor.fetchone()
            
            if row:
                cursor.execute('''
                    UPDATE baseline_network 
                    SET last_seen = ?, count = count + 1 
                    WHERE remote_ip = ?
                ''', (now, remote_ip))
            else:
                cursor.execute('''
                    INSERT INTO baseline_network (remote_ip, first_seen, last_seen, count)
                    VALUES (?, ?, ?, 1)
                ''', (remote_ip, now, now))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Error updating network baseline: {e}")
        finally:
            conn.close()

    def is_new(self, remote_ip: str) -> bool:
        """
        Checks if a remote IP is new.
        """
        if not remote_ip:
            return False

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM baseline_network WHERE remote_ip = ?', (remote_ip,))
        row = cursor.fetchone()
        conn.close()
        
        return row is None
