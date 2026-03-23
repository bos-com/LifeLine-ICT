LifeLine-ICT
Project Summary
LifeLine-ICT is a digital infrastructure management platform designed to support university ICT departments. The system tracks strategic ICT projects, inventory assets, IoT deployments, and maintenance activities to ensure digital services remain reliable for students and researchers. This repository contains the code for the IoT device layer, backend APIs, and documentation required for faculties to adapt the platform to their own campuses.

High-Level Architecture
The solution consists of five collaborating layers:

IoT Layer: ESP32-based sensor nodes that send telemetry to a lightweight Flask logger (iot/logging).

Backend APIs: A FastAPI service (backend/app) providing CRUD endpoints for projects, resources, locations, maintenance tickets, and sensor sites.

GIS & Analytics: Future modules intended to combine telemetry and asset data for dashboards and risk assessments.

Frontend: Web dashboards and mobile applications that consume the backend APIs.

Deployment: Infrastructure-as-code scripts to package the stack for on-campus or cloud hosting.

Refer to docs/backend_crud_plan.md for the architectural rationale regarding the CRUD API implementation.

Module Overview
iot/: Firmware sketches and logging scripts for field sensors.

backend/: FastAPI application, domain models, services, and tests.

docs/: Supplemental guides and design notes.

Planned Directories: Frontend, GIS, and Deployment modules will be added as the initiative matures.

Backend Service
Prerequisites
Python 3.11+

pip or uv for dependency management

Optional: uvicorn CLI for local development

Installation
Bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
Running the API
Bash
uvicorn backend.app.main:app --reload
The service runs on http://127.0.0.1:8000 by default. Interactive OpenAPI documentation is available at http://127.0.0.1:8000/docs.

Core Endpoints
Entity	Base Path	Notes
Projects	/api/v1/projects	CRUD with pagination and search functionality.
ICT Resources	/api/v1/resources	Validates project/location references and enforces ticket rules.
Locations	/api/v1/locations	CRUD with geographic metadata.
Maintenance Tickets	/api/v1/maintenance-tickets	Requires resolution metadata when closing a ticket.
Sensor Sites	/api/v1/sensor-sites	Links IoT deployments to resources, projects, and locations.
All list endpoints support limit, offset, and search query parameters and return pagination metadata.

Running Tests
Bash
pytest backend/tests
The test suite utilizes an in-memory SQLite database and covers service-level rules, such as preventing resource deletion while maintenance tickets remain open.

Database Migrations
This project uses Alembic for database migrations.

To create a new migration:

Bash
alembic revision --autogenerate -m "migration_message"
To apply migrations:

Bash
alembic upgrade head
Data Model Highlights
The backend models capture several key relationships:

Projects aggregate ICT resources and sensor sites.

Resources can link to projects and locations and host sensor deployments.

Maintenance Tickets are assigned to resources and require closure notes upon resolution.

Contributing
Create a new issue or select an existing one from the issue tracker.

Branch from main: git checkout -b feature/your-feature-name.

Maintain the layered structure (api, services, repositories, models) to keep the codebase organized.

Write tests and verify they pass using pytest backend/tests before opening a pull request.

Document any behavior changes in code docstrings or project documentation.

License
This project is dual-licensed under MIT and Apache licenses.

Maintainers
Muwanga Erasto Kosea

Ouma Ronald