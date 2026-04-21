"""
LifeLine-ICT IoT Sensor Logger
A lightweight Flask service that receives and stores
telemetry data from ESP32 field sensor nodes.
"""

from flask import Flask, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'telemetry.db')


def init_db():
    """Initialize the SQLite database and create the telemetry table."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id   TEXT    NOT NULL,
            temperature REAL,
            humidity    REAL,
            flood_level REAL,
            timestamp   TEXT    NOT NULL,
            received_at TEXT    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "LifeLine-ICT IoT Logger"}), 200


@app.route('/log', methods=['POST'])
def log_telemetry():
    """
    Receive telemetry data from an ESP32 sensor node.

    Expected JSON payload:
    {
        "sensor_id":   "ESP32-001",
        "temperature": 24.5,
        "humidity":    68.2,
        "flood_level": 12.3,
        "timestamp":   "2026-04-21T10:30:00Z"
    }
    """
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    sensor_id = data.get('sensor_id')
    if not sensor_id:
        return jsonify({"error": "sensor_id is required"}), 400

    temperature = data.get('temperature')
    humidity    = data.get('humidity')
    flood_level = data.get('flood_level')
    timestamp   = data.get('timestamp', datetime.utcnow().isoformat())
    received_at = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO telemetry
            (sensor_id, temperature, humidity, flood_level, timestamp, received_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (sensor_id, temperature, humidity, flood_level, timestamp, received_at))
    conn.commit()
    conn.close()

    return jsonify({
        "status":    "logged",
        "sensor_id": sensor_id,
        "received":  received_at
    }), 201


@app.route('/logs', methods=['GET'])
def get_logs():
    """Return the 50 most recent telemetry entries."""
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        'SELECT * FROM telemetry ORDER BY received_at DESC LIMIT 50'
    )
    rows = cursor.fetchall()
    conn.close()

    logs = [
        {
            "id":          row[0],
            "sensor_id":   row[1],
            "temperature": row[2],
            "humidity":    row[3],
            "flood_level": row[4],
            "timestamp":   row[5],
            "received_at": row[6],
        }
        for row in rows
    ]
    return jsonify({"count": len(logs), "logs": logs}), 200


if __name__ == '__main__':
    init_db()
    print("LifeLine-ICT IoT Logger running on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)