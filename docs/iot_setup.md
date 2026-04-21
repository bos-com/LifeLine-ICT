# IoT Sensor Setup Guide

This guide covers setting up the ESP32 sensor nodes and the Flask logging service.

## Flask Logger Setup

```bash
cd iot/logging
python -m venv .venv
source .venv/bin/activate
pip install flask
python app.py
```

Logger runs at: `http://0.0.0.0:5000`

## Endpoints

| Method | Endpoint  | Description                  |
|--------|-----------|------------------------------|
| POST   | /log      | Receive sensor telemetry     |
| GET    | /health   | Check logger status          |
| GET    | /logs     | View recent log entries      |

## Sending Data from ESP32

Configure your ESP32 sketch with:
```cpp
const char* serverUrl = "http://YOUR-SERVER-IP:5000/log";
```

## Sample Payload

```json
{
  "sensor_id": "ESP32-001",
  "temperature": 24.5,
  "humidity": 68.2,
  "flood_level": 12.3,
  "timestamp": "2026-04-21T10:30:00Z"
}
```

## Data Storage

Telemetry is stored in SQLite at `iot/logging/telemetry.db`