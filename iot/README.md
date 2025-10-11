# IoT Layer for LifeLine-ICT

This directory contains the code and documentation for the IoT layer of the LifeLine-ICT project.

## Purpose
- Collect telemetry from ESP32-based sensor nodes (or similar devices)
- Log sensor data to a local or remote endpoint
- Provide a simple ingestion API for the backend

## Structure
- `logging/` — Python scripts for receiving and logging sensor data
- `firmware/` — Example Arduino/ESP32 sketches for sending data

## Getting Started
1. See `logging/` for a sample Flask-based ingestion server
2. See `firmware/` for example device code

---

For details, see issue #2 in the main repository.
