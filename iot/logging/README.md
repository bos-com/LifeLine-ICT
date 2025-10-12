# IoT Logging Server

This is a simple Flask-based server for ingesting sensor data from IoT devices (e.g., ESP32).

## Usage

1. Install dependencies:
   ```bash
   pip install flask
   ```
2. Run the server:
   ```bash
   python log_data.py
   ```
3. The server will listen on port 5000 for POST requests to `/data`.

## Example Payload
```
{
  "sensor_id": 1,
  "metric": "temperature",
  "value": 23.5,
  "timestamp": "2025-10-11T12:00:00Z"
}
```

All received data is logged to `logs/sensor_data.log`.
