# IoT Setup Guide

This guide explains how to set up and run the IoT layer of LifeLine-ICT locally.

## Prerequisites
- Python 3.8 or higher installed
- pip package manager
- A stable internet connection

## Step 1 — Clone the Repository
```bash
git clone https://github.com/bos-com/LifeLine-ICT.git
cd LifeLine-ICT
```

## Step 2 — Install Dependencies
```bash
cd iot
pip install -r requirements.txt
```

## Step 3 — Configure Environment Variables
Copy the example environment file and update it with your settings:
```bash
cp .env.example .env
```
Open the .env file and set the following:
- FLASK_ENV=development
- MQTT_BROKER=your_broker_address
- SENSOR_PORT=your_sensor_port

## Step 4 — Run the Flask Ingestion Server
```bash
python app.py
```
The server will start on http://localhost:5000

## Step 5 — Test the IoT Connection
Send a test sensor reading to verify the server is receiving data:
```bash
curl -X POST http://localhost:5000/sensor-data \
-H "Content-Type: application/json" \
-d '{"sensor_id": "001", "value": 23.5, "type": "temperature"}'
```
A successful response confirms the IoT layer is running correctly.

## Troubleshooting
- If the server fails to start, check that all dependencies are installed.
- If sensor data is not received, verify your MQTT broker address in the .env file.
