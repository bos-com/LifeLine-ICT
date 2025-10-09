
from flask import Flask, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

# --- Configuration ---
LOG_FILE = 'sensor_data.csv'

# --- CSV Header ---
CSV_HEADER = ['timestamp', 'sensor_type', 'value']

# --- Initialize CSV file ---
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)

@app.route('/data', methods=['POST'])
def log_data():
    """Receives sensor data and logs it to a CSV file."""
    try:
        data = request.get_json()
        if not data or 'sensor_type' not in data or 'value' not in data:
            return jsonify({'error': 'Invalid payload'}), 400

        timestamp = datetime.utcnow().isoformat()
        sensor_type = data['sensor_type']
        value = data['value']

        # --- Log to console ---
        print(f"Received data: {timestamp}, {sensor_type}, {value}")

        # --- Append to CSV ---
        with open(LOG_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, sensor_type, value])

        return jsonify({'status': 'success'}), 201

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    # To install dependencies: pip install Flask
    # To run: python log_data.py
    app.run(host='0.0.0.0', port=5000, debug=True)
