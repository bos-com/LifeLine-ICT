# IoT Sensor Deployment Guide

This guide explains how to set up, configure, and deploy ESP32-based sensor
nodes for the LifeLine-ICT early-warning system.

## Architecture Overview

```
┌──────────────┐     HTTP POST      ┌─────────────────┐     REST API      ┌──────────────┐
│  ESP32 Node  │ ─────────────────> │  Flask Logger    │ ────────────────> │ FastAPI       │
│  (Sensors)   │   /api/log         │  (iot/logging)   │   /api/v1/...    │ Backend       │
└──────────────┘                    └─────────────────┘                   └──────────────┘
       │                                    │                                     │
  Reads sensor                        Validates &                          Stores in DB,
  data (temp,                         timestamps                           links to
  humidity, etc.)                     telemetry                            sensor sites
```

The data flows in three stages:

1. **ESP32 nodes** read environmental sensors and POST JSON payloads to the
   Flask logger.
2. **Flask logger** (`iot/logging/`) validates incoming data, adds timestamps,
   and optionally forwards records to the FastAPI backend.
3. **FastAPI backend** (`backend/app/`) persists sensor readings and exposes
   them through the Sensor Sites API.

## Hardware Requirements

| Component               | Specification          | Purpose                        |
|-------------------------|------------------------|--------------------------------|
| ESP32 DevKit v1         | Dual-core, Wi-Fi       | Main microcontroller           |
| DHT22 sensor            | Temp + humidity         | Environmental monitoring       |
| Rain gauge (tipping)    | Digital pulse output    | Rainfall measurement           |
| Water level sensor      | Analog 0-5 V           | Flood detection                |
| 5 V USB power supply    | ≥ 1 A                  | Board power                    |
| Breadboard + jumper wires | Standard              | Prototyping connections        |

## Wiring Reference (DHT22 Example)

```
ESP32 Pin    DHT22 Pin    Notes
─────────    ─────────    ──────────────────────────
3V3          VCC (1)      Power supply
GPIO 4       DATA (2)     Add a 10 kΩ pull-up to 3V3
GND          GND (4)      Common ground
             NC (3)       Not connected
```

For the water-level analog sensor, connect the signal wire to any ADC-capable
GPIO (e.g., GPIO 34) and power from the 5 V USB rail.

## Firmware Setup

### Prerequisites

- Arduino IDE 2.x or PlatformIO
- ESP32 board package installed
- Required libraries: `WiFi.h`, `HTTPClient.h`, `DHT.h`

### Configuration

Edit the constants at the top of the firmware sketch before flashing:

```cpp
// Wi-Fi credentials
const char* WIFI_SSID     = "your_network";
const char* WIFI_PASSWORD = "your_password";

// Flask logger endpoint
const char* SERVER_URL = "http://192.168.1.100:5000/api/log";

// Sensor reading interval (milliseconds)
const unsigned long INTERVAL = 60000;  // 1 minute
```

### Flashing

1. Connect the ESP32 via USB.
2. Select the correct board and COM port in your IDE.
3. Upload the sketch.
4. Open the Serial Monitor at 115200 baud to verify connectivity.

## Flask Logger Configuration

The logger lives in `iot/logging/` and accepts sensor telemetry via HTTP.

### Environment Variables

Create a `.env` file in `iot/logging/`:

```bash
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
LOG_FILE=sensor_data.log

# Optional: forward to the backend API
BACKEND_URL=http://localhost:8000/api/v1/sensor-sites
BACKEND_API_KEY=your_api_key_here
```

### Running the Logger

```bash
cd iot/logging
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The logger listens on `http://0.0.0.0:5000/api/log`.

### Testing with curl

```bash
curl -X POST http://localhost:5000/api/log \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "esp32-node-01",
    "temperature": 28.5,
    "humidity": 65.2,
    "water_level": 0.3,
    "timestamp": "2025-06-15T14:30:00Z"
  }'
```

## Sensor Thresholds

Configure alert thresholds based on local conditions:

| Parameter     | Normal Range   | Warning        | Critical       |
|---------------|----------------|----------------|----------------|
| Temperature   | 15–35 °C       | 35–40 °C       | > 40 °C        |
| Humidity      | 30–80 %        | 80–90 %        | > 90 %         |
| Water level   | 0.0–0.5 m      | 0.5–1.0 m      | > 1.0 m        |
| Rainfall rate | 0–10 mm/hr     | 10–30 mm/hr    | > 30 mm/hr     |

These thresholds should be adjusted for each deployment site based on
historical climate data and local geography.

## Field Deployment Checklist

- [ ] ESP32 powered and connected to Wi-Fi
- [ ] Serial monitor shows successful HTTP POSTs
- [ ] Flask logger is reachable from the sensor network
- [ ] Sensor readings appear in the backend API
- [ ] Enclosure is weatherproof (IP65 or better for outdoor use)
- [ ] Power supply has battery backup for continuous monitoring

## Troubleshooting

| Symptom                              | Likely Cause                  | Fix                                    |
|--------------------------------------|-------------------------------|----------------------------------------|
| ESP32 won't connect to Wi-Fi         | Wrong SSID/password           | Double-check credentials in firmware   |
| HTTP POST returns 404                | Wrong logger URL or port      | Verify `SERVER_URL` and Flask is running |
| Sensor reads 0 or NaN               | Loose wiring or wrong GPIO    | Re-check wiring, add pull-up resistor  |
| Logger runs but backend has no data  | `BACKEND_URL` not configured  | Set environment variable in `.env`     |
| High latency between readings        | Network congestion            | Reduce payload size or increase interval |
