# IoT Sensor Logger

Lightweight Flask service that receives telemetry from ESP32 sensor nodes
and stores it in SQLite for the LifeLine-ICT platform.

## Run

```bash
pip install -r requirements.txt
python app.py
```

## Endpoints

- `GET  /health` — Check service is running
- `POST /log`    — Submit sensor telemetry (JSON)
- `GET  /logs`   — View last 50 telemetry records

## Sample Request

```bash
curl -X POST http://localhost:5000/log \
  -H "Content-Type: application/json" \
  -d '{"sensor_id":"ESP32-001","temperature":24.5,"humidity":68.2,"flood_level":12.3}'
```