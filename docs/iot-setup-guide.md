# IoT Setup Guide — LifeLine-ICT

This guide walks new developers through setting up the ESP32-based IoT sensor layer used in LifeLine-ICT. The IoT layer collects environmental telemetry (temperature, humidity, flood/drought indicators) and forwards it to the Flask logging service for storage and analysis.

---

##  Hardware Requirements

| Component | Specification | Purpose |
|-----------|--------------|---------|
| ESP32 Dev Board | ESP32-WROOM-32 or equivalent | Main microcontroller |
| DHT22 Sensor | Digital temperature & humidity | Environmental monitoring |
| Water Level Sensor | Analog resistive type | Flood/drought detection |
| Jumper Wires | Male-to-male and male-to-female | Connections |
| USB Cable | Micro-USB or USB-C (board dependent) | Programming & power |
| Power Supply | 5V via USB or 3.3V LiPo | Field deployment power |

---

##  Software Prerequisites

Install the following on your development machine:

- **Arduino IDE** 2.0+ or **PlatformIO** (VS Code extension recommended)
- **Python 3.11+** — for running the Flask telemetry logger
- **Git** — for cloning the repository
- **CP210x USB Driver** — for ESP32 serial communication ([download here](https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers))

### Arduino IDE Board Setup

1. Open Arduino IDE → **File** → **Preferences**
2. Add this URL to "Additional boards manager URLs":
3. 3. Go to **Tools** → **Board** → **Boards Manager**
4. Search for `esp32` and install **esp32 by Espressif Systems**

### Required Arduino Libraries

Install via **Tools** → **Manage Libraries**:

| Library | Version | Purpose |
|---------|---------|---------|
| DHT sensor library | 1.4.4+ | Reading DHT22 sensor |
| Adafruit Unified Sensor | 1.1.9+ | Sensor abstraction layer |
| ArduinoJson | 6.x | JSON payload formatting |
| WiFi (built-in) | — | ESP32 Wi-Fi connectivity |
| HTTPClient (built-in) | — | Sending data to Flask logger |

---

##  Hardware Wiring

Connect the components to the ESP32 as follows:

### DHT22 Sensor
### Water Level Sensor
---

##  Firmware Configuration

### Step 1 — Clone the Repository

```bash
git clone https://github.com/bos-com/LifeLine-ICT.git
cd LifeLine-ICT/iot
```

### Step 2 — Configure Wi-Fi and Server Settings

Open the firmware sketch file (e.g., `iot/sensor_node/sensor_node.ino`) and update the configuration section at the top:

```cpp
// ── Wi-Fi Configuration ──────────────────────────────────────
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// ── Flask Logger Server ──────────────────────────────────────
const char* SERVER_URL    = "http://YOUR_SERVER_IP:5000/log";

// ── Sensor Settings ──────────────────────────────────────────
const int   DHT_PIN       = 4;
const int   WATER_PIN     = 34;
const int   SEND_INTERVAL = 30000;  // milliseconds between readings
```

Replace `YOUR_WIFI_SSID`, `YOUR_WIFI_PASSWORD`, and `YOUR_SERVER_IP` with your actual values.

### Step 3 — Flash the Firmware

1. Connect the ESP32 to your computer via USB
2. In Arduino IDE: **Tools** → **Board** → select `ESP32 Dev Module`
3. **Tools** → **Port** → select the correct COM port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux)
4. Click **Upload** ( button)
5. Open **Serial Monitor** (baud rate: `115200`) to verify sensor readings

---

##  Setting Up the Flask Telemetry Logger

The IoT devices send data to a lightweight Flask service located in `iot/logging/`.

### Step 1 — Install Dependencies

```bash
cd LifeLine-ICT/iot/logging
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2 — Configure the Logger

```bash
cp .env.example .env
```

Edit `.env`:
```env
FLASK_PORT=5000
FLASK_DEBUG=true
DB_PATH=./telemetry.db       # SQLite path for local dev
LOG_LEVEL=INFO
```

### Step 3 — Start the Logger

```bash
python app.py
```

The logger listens on `http://0.0.0.0:5000`. Incoming sensor payloads are accepted at `POST /log`.

### Expected Payload Format

The ESP32 sends JSON like this:

```json
{
  "device_id": "node-001",
  "site_id": "campus-north",
  "timestamp": "2026-04-01T10:30:00Z",
  "temperature_c": 27.4,
  "humidity_pct": 68.2,
  "water_level_raw": 312,
  "water_level_pct": 45.6
}
```

---

##  Verifying the Full Pipeline

1. Start the Flask logger
2. Power on the ESP32 (or open Serial Monitor to watch output)
3. After `SEND_INTERVAL` ms, the ESP32 sends a reading
4. Check the logger terminal — you should see an incoming `POST /log` request
5. Verify data was saved: `sqlite3 telemetry.db "SELECT * FROM readings LIMIT 5;"`

---

##  Connecting to the Backend API

Once telemetry is being collected by the Flask logger, the FastAPI backend (`backend/app`) ingests it and links readings to **Sensor Sites** in the data model. See the [API Reference](api-reference.md) for the `/api/v1/sensor-sites` endpoint.

---

##  Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| ESP32 not detected | Missing USB driver | Install CP210x driver |
| Upload fails | Wrong board or port selected | Check Tools → Board and Port |
| "WiFi connection failed" | Wrong credentials | Double-check SSID/password in firmware |
| No data in Flask logs | Wrong SERVER_URL | Ensure IP address and port are correct |
| Sensor reads -999 | DHT22 wiring issue | Check DATA pin connection to GPIO 4 |
| Water level always 0 | ADC pin issue | Confirm SIG connects to GPIO 34 |

---

##  Getting Help

Open an issue at: https://github.com/bos-com/LifeLine-ICT/issues

Tag it with `iot` and include your board type, Arduino IDE version, and Serial Monitor output.
