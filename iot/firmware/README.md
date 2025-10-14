# ESP32 Sensor Example

This directory contains an example Arduino sketch for an ESP32 device that sends sensor data to the LifeLine-ICT backend ingestion endpoint.

## Usage
1. Open `esp32_sensor_example.ino` in the Arduino IDE.
2. Set your WiFi credentials and the server URL at the top of the file.
3. Upload the sketch to your ESP32.
4. The device will send a JSON payload to the backend every 60 seconds.

## Example Payload
```
{
  "sensor_id": 1,
  "metric": "temperature",
  "value": 23.5,
  "timestamp": "2025-10-11T12:00:00Z"
}
```

You can modify the payload to match your sensor and metric.
