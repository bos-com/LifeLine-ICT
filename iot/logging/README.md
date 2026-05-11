# IoT Logging Server

This is a simple Flask-based server for ingesting sensor data from IoT devices (e.g., ESP32).

## Prerequisites

- Python 3.11+
- `pip`
- Network access from the sensor device to the machine running the logger

## Setup

1. Install dependencies:
   ```bash
   pip install flask
   ```
2. Run the server:
   ```bash
   python log_data.py
   ```
3. The server will listen on port 5000 for POST requests to `/data`.

Debug mode is disabled by default so the logger is safer to run on shared
campus networks. Enable it only for local development:

```bash
FLASK_DEBUG=true python log_data.py
```

## Test Request

Use `curl` to confirm the logger accepts JSON payloads:

```bash
curl -X POST http://127.0.0.1:5000/data \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":1,"metric":"temperature","value":23.5}'
```

Successful responses include `status` and a UTC timestamp.

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

## Operational Notes

- Keep the logger behind a trusted campus network or reverse proxy.
- Rotate or archive `logs/sensor_data.log` if the service runs continuously.
- Avoid enabling `FLASK_DEBUG` outside local development.
