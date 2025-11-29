from flask import Flask, jsonify, request
import threading
from ..config.loader import APIConfig
from ..storage.db import DatabaseManager
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class APIServer(threading.Thread):
    def __init__(self, config: APIConfig, db_path: str):
        super().__init__()
        self.config = config
        self.app = Flask(__name__)
        self.db = DatabaseManager(db_path)
        self.daemon = True
        
        self._register_routes()

    def _register_routes(self):
        @self.app.route('/status', methods=['GET'])
        def status():
            return jsonify({"status": "running"})

        @self.app.route('/alerts', methods=['GET'])
        def get_alerts():
            # Fetch all alerts (enriched and unenriched)
            # This is a simplified fetch. In real world, we'd add filtering.
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 50')
            rows = cursor.fetchall()
            
            alerts = []
            for row in rows:
                # Fetch enrichment if exists
                enrichment = {}
                if row[6]: # is_enriched
                    cursor.execute('SELECT * FROM enrichments WHERE alert_id = ?', (row[0],))
                    enrich_row = cursor.fetchone()
                    if enrich_row:
                        enrichment = {
                            "summary": enrich_row[1],
                            "severity_score": enrich_row[2],
                            "threat_category": enrich_row[3],
                            "recommendations": enrich_row[4]
                        }

                alerts.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "severity": row[2],
                    "rule_name": row[3],
                    "description": row[4],
                    "is_enriched": bool(row[6]),
                    "enrichment": enrichment
                })
            conn.close()
            return jsonify(alerts)

        @self.app.route('/alerts/<int:alert_id>', methods=['GET'])
        def get_alert_detail(alert_id):
            conn = self.db._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
            row = cursor.fetchone()
            
            if not row:
                conn.close()
                return jsonify({"error": "Alert not found"}), 404

            alert = {
                "id": row[0],
                "timestamp": row[1],
                "severity": row[2],
                "rule_name": row[3],
                "description": row[4],
                "related_events": row[5],
                "is_enriched": bool(row[6])
            }
            
            if alert['is_enriched']:
                cursor.execute('SELECT * FROM enrichments WHERE alert_id = ?', (alert_id,))
                enrich_row = cursor.fetchone()
                if enrich_row:
                    alert['enrichment'] = {
                        "summary": enrich_row[1],
                        "severity_score": enrich_row[2],
                        "threat_category": enrich_row[3],
                        "recommendations": enrich_row[4]
                    }
            
            conn.close()
            return jsonify(alert)

    def run(self):
        logger.info(f"Starting API server on {self.config.host}:{self.config.port}")
        self.app.run(host=self.config.host, port=self.config.port, debug=False, use_reloader=False)

    def stop(self):
        pass
