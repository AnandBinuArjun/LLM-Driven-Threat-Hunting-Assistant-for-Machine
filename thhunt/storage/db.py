import sqlite3
import os
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    def _init_db(self):
        """
        Initialize database schema.
        """
        logger.info(f"Initializing database at {self.db_path}")
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                host_id TEXT,
                category TEXT,
                event_type TEXT,
                raw_data JSON
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                severity TEXT,
                rule_name TEXT,
                description TEXT,
                related_events JSON,
                is_enriched BOOLEAN DEFAULT 0
            )
        ''')

        # Enrichments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrichments (
                alert_id INTEGER PRIMARY KEY,
                summary TEXT,
                severity_score INTEGER,
                threat_category TEXT,
                recommendations TEXT,
                FOREIGN KEY(alert_id) REFERENCES alerts(id)
            )
        ''')

        conn.commit()
        conn.close()

    def insert_event(self, event: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        # TODO: Proper normalization and insertion
        # For now just dumping raw
        import json
        cursor.execute('''
            INSERT INTO events (timestamp, host_id, category, event_type, raw_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (event.get('timestamp'), event.get('host_id', 'unknown'), event.get('category', 'unknown'), event.get('type'), json.dumps(event)))
        conn.commit()
        conn.close()

    def insert_alert(self, alert: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (timestamp, severity, rule_name, description, related_events, is_enriched)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert.get('timestamp'), alert.get('severity'), alert.get('rule_name'), alert.get('description'), alert.get('related_events'), alert.get('is_enriched')))
        conn.commit()
        conn.close()

    def get_unenriched_alerts(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alerts WHERE is_enriched = 0')
        rows = cursor.fetchall()
        # Convert to dicts
        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "timestamp": row[1],
                "severity": row[2],
                "rule_name": row[3],
                "description": row[4],
                "related_events": row[5],
                "is_enriched": row[6]
            })
        conn.close()
        return alerts

    def update_alert_enrichment(self, alert_id: int, enrichment: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Update alert status
        cursor.execute('UPDATE alerts SET is_enriched = 1, severity = ? WHERE id = ?', (enrichment.get('severity_score'), alert_id))
        
        # Insert enrichment details
        cursor.execute('''
            INSERT INTO enrichments (alert_id, summary, severity_score, threat_category, recommendations)
            VALUES (?, ?, ?, ?, ?)
        ''', (alert_id, enrichment.get('summary'), enrichment.get('severity_score'), enrichment.get('threat_category'), enrichment.get('recommendations')))
        
        conn.commit()
        conn.close()
