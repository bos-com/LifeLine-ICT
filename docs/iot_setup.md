
# IoT Device Setup Guide

This guide provides instructions for setting up, configuring, and deploying the IoT sensors for the LifeLine-ICT project.

## 1. Overview

The IoT layer consists of two main components:

1.  **Sensor Nodes**: ESP32 microcontrollers connected to rainfall and water level sensors.
2.  **Data Logger**: A Python script that acts as a simple backend to receive and log data from the sensors.

## 2. Hardware Requirements

*   **Microcontroller**: ESP32 Development Board
*   **Rainfall Sensor**: Tipping Bucket Rain Gauge (connected to a digital GPIO pin)
*   **Water Level Sensor**: HC-SR04 Ultrasonic Sensor

## 3. Sensor Code Setup (Arduino)

The code for the sensors is written in C++ using the Arduino framework.

### 3.1. Prerequisites

*   [Arduino IDE](https://www.arduino.cc/en/software) or [PlatformIO](https://platformio.org/)
*   ESP32 Board Support Package installed in your IDE.
*   Libraries: `WiFi`, `HTTPClient` (usually included with the ESP32 package).

### 3.2. Configuration

There are two sketch files located in `iot/sensors/`:

*   `rainfall_sensor.ino`
*   `water_level_sensor.ino`

In both files, you **must** update the following configuration variables at the top of the file:

```cpp
// --- Configuration ---
const char* ssid = "YOUR_WIFI_SSID";         // Your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password
const char* api_endpoint = "http://<YOUR_SERVER_IP>:5000/data"; // URL of the data logger
```

### 3.3. Pin Configuration

*   **Rainfall Sensor**: The `rain_sensor_pin` is set to `GPIO14`. You can change this if needed.
*   **Water Level Sensor**: The `trig_pin` and `echo_pin` are set to `GPIO12` and `GPIO13` respectively.

### 3.4. Uploading the Code

1.  Open the desired `.ino` file in your IDE.
2.  Select your ESP32 board from the board manager.
3.  Select the correct COM port.
4.  Click "Upload" to flash the code to the ESP32.

## 4. Data Logger Setup (Python)

The data logger is a simple Flask web server that listens for incoming data from the sensors and logs it to a CSV file.

### 4.1. Prerequisites

*   Python 3.x
*   Flask library

### 4.2. Installation

Navigate to the `iot/logging/` directory and install Flask:

```bash
pip install Flask
```

### 4.3. Running the Server

From the `iot/logging/` directory, run the following command:

```bash
python log_data.py
```

The server will start and listen on all network interfaces at `http://0.0.0.0:5000`.

### 4.4. Logged Data

Sensor data will be appended to the `sensor_data.csv` file in the `iot/logging/` directory. The file will have the following columns:

*   `timestamp`
*   `sensor_type`
*   `value`
