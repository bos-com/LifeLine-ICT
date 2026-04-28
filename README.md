# LifeLine-ICT

## 📌 Project Overview

LifeLine-ICT is a digital infrastructure management platform designed to support university ICT departments in managing and maintaining their technology ecosystems.  

The system enables tracking of:
- ICT projects
- Hardware and software assets
- IoT deployments
- Maintenance operations  

It improves reliability, visibility, and decision-making for campus digital services used by students, staff, and researchers.

---

## 🏗️ High-Level Architecture

The platform is built using a layered architecture:

- **IoT Layer**  
  ESP32-based sensor nodes collect and send telemetry data to a Flask logging service.

- **Backend APIs**  
  A FastAPI backend provides RESTful APIs for managing projects, resources, locations, and maintenance.

- **GIS & Analytics (Planned)**  
  Future modules will support dashboards, analytics, and risk monitoring.

- **Frontend (Planned)**  
  Web and mobile applications will interact with backend APIs.

- **Deployment (Planned)**  
  Infrastructure-as-code for cloud or on-campus deployment.

---

## 📁 Project Structure
