"""
Flask-based ingestion endpoint for LifeLine-ICT IoT sensor data.

Receives POST requests from ESP32 or similar devices and logs the data.
"""

from flask import Flask, request, jsonify
import logging
from datetime import datetime
import os

app = Flask(__name__)

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/sensor_data.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

@app.route("/data", methods=["POST"])
def ingest_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload received"}), 400
    # Log the data
    logging.info(f"Received data: {data}")
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
