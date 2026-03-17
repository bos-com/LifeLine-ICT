# LifeLine-ICT

## Project Summary

LifeLine-ICT is a digital infrastructure management platform that supports the
Uganda University ICT department. The system tracks strategic ICT projects,
inventory assets, IoT deployments, and the maintenance activities that keep
digital services reliable for students and researchers. The repository contains
code for the IoT device layer, the backend APIs, and supporting documentation so
faculties can adapt the platform to their own campuses.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- `pip` or `uv` for dependency management
- PostgreSQL (for production)
- Docker & Docker Compose (recommended)

### Running with Docker

```bash
# Clone the repository
git clone https://github.com/bos-com/LifeLine-ICT.git
cd LifeLine-ICT

# Start the backend service
docker-compose up -d

# Access the API
# API: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
```

---

## 🏗️ Architecture

The solution comprises five collaborating layers:

- **IoT layer** – ESP32-based sensor nodes send telemetry to a lightweight Flask
  logger (`iot/logging`).
- **Backend APIs** – A FastAPI service (`backend/app`) exposes CRUD endpoints for
  projects, resources, locations, maintenance tickets, and sensor sites.
- **GIS & Analytics** – Future modules will combine telemetry and asset data to
  power dashboards and risk assessments.
- **Frontend** – Web dashboards and mobile apps consume the backend APIs.
- **Deployment** – Infrastructure-as-code scripts will package the stack for on
  campus or cloud hosting.

### Module Overview

- `iot/` – Firmware sketches and logging scripts for field sensors.
- `backend/` – FastAPI application, domain models, services, and tests.
- `docs/` – Supplemental guides and design notes.
- Additional directories (frontend, gis, deployment) will be filled as the
  broader initiative matures.

---

## 🛠️ Backend Service Setup

### Prerequisites

- Python 3.11+
- `pip` or `uv` for dependency management
- Optional: `uvicorn` CLI for local development

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### Running the API

```bash
uvicorn backend.app.main:app --reload
```

The service listens on `http://127.0.0.1:8000` by default. OpenAPI
documentation is available at `http://127.0.0.1:8000/docs`.

### Core Endpoints

| Entity | Base Path | Notes |
| --- | --- | --- |
| Projects | `/api/v1/projects` | CRUD with pagination & search |
| ICT Resources | `/api/v1/resources` | Validates project/location references and enforces ticket rules |
| Locations | `/api/v1/locations` | CRUD with geo metadata |
| Maintenance Tickets | `/api/v1/maintenance-tickets` | Requires resolution metadata when closing a ticket |
| Sensor Sites | `/api/v1/sensor-sites` | Links IoT deployments to resources, projects, and locations |

Each list endpoint accepts `limit`, `offset`, and `search` query parameters and
returns pagination metadata to keep API consumers informed.

### Running Tests

```bash
pytest backend/tests
```

The suite provisions an in-memory SQLite database and covers both service-level
rules (such as blocking resource deletion while tickets remain open) and API
contracts.

### Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/en/latest/) for database migrations.

To create a new migration, run:

```bash
alembic revision --autogenerate -m "<migration_message>"
```

To apply migrations to the database, run:

```bash
alembic upgrade head
```

### Data Model Highlights

The backend models capture the following relationships:

- Projects aggregate ICT resources and sensor sites.
- Resources optionally link to projects and locations, and can host sensor
  deployments.
- Maintenance tickets belong to resources and require closure notes when marked
  resolved.

Consult the service-layer docstrings for detailed business rules and
institutional context.

---

## 🧰 Technologies

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Migrations**: Alembic
- **Testing**: pytest
- **IoT**: ESP32, Flask
- **Documentation**: OpenAPI/Swagger

---

## 🤝 Contributing

1. Create an issue or pick an existing one (see GitHub Issues).
2. Branch from `main`: `git checkout -b feature/your-feature`.
3. Follow the layered structure (`api`, `services`, `repositories`, `models`) to
   keep contributions organised.
4. Write tests and run `pytest backend/tests` before opening a pull request.
5. Document behaviour changes in code docstrings or the project docs.

---

## 📄 License

MIT, Apache

## 👥 Maintainers

Muwanga Erasto Kosea, Ouma Ronald
