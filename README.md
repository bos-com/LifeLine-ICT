# LifeLine-ICT

LifeLine-ICT is a digital infrastructure management platform for the Uganda
University ICT department. It tracks strategic ICT projects, inventory assets,
IoT deployments, locations, and maintenance activities that keep digital
services reliable for students and researchers.

## Architecture Overview

- **IoT layer**: ESP32-based sensor nodes and a lightweight Flask logger under
  `iot/`.
- **Backend APIs**: A FastAPI service under `backend/app` exposes CRUD endpoints
  for projects, resources, locations, maintenance tickets, and sensor sites.
- **GIS and analytics**: Future modules can combine telemetry and asset data for
  dashboards and risk assessment.
- **Frontend**: Planned web and mobile clients can consume the backend APIs.
- **Deployment**: Future infrastructure scripts can package the stack for campus
  or cloud hosting.

## Repository Structure

```text
LifeLine-ICT/
├── backend/              # FastAPI app, SQLAlchemy models, services, and tests
├── docs/                 # Backend plans and design notes
├── iot/                  # Firmware and telemetry logging examples
├── plan.md               # Project planning notes
└── README.md             # Project overview and setup guide
```

## Backend Prerequisites

- Python 3.11+
- `pip` or another Python package manager
- Optional: `uvicorn` CLI for local development

## Backend Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   On macOS or Linux, use `source .venv/bin/activate`.

2. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the API:

   ```bash
   uvicorn backend.app.main:app --reload
   ```

4. Open the local API documentation:

   - Swagger UI: `http://127.0.0.1:8000/docs`
   - OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Core API Endpoints

| Entity | Base Path | Notes |
| --- | --- | --- |
| Projects | `/api/v1/projects` | CRUD with pagination and search |
| ICT Resources | `/api/v1/resources` | Validates project and location references |
| Locations | `/api/v1/locations` | CRUD with geographic metadata |
| Maintenance Tickets | `/api/v1/maintenance-tickets` | Requires closure metadata when resolving tickets |
| Sensor Sites | `/api/v1/sensor-sites` | Links IoT deployments to resources, projects, and locations |

List endpoints accept `limit`, `offset`, and `search` query parameters and
return pagination metadata for API clients.

## Database Migrations

LifeLine-ICT uses Alembic for database migrations.

```bash
alembic -c backend/alembic.ini revision --autogenerate -m "describe_change"
alembic -c backend/alembic.ini upgrade head
```

## Testing

```bash
pytest backend/tests
```

The test suite provisions an in-memory SQLite database and covers service-level
rules plus API contracts.

## Documentation

- [`docs/backend_crud_plan.md`](docs/backend_crud_plan.md) explains the backend
  CRUD architecture.
- [`iot/README.md`](iot/README.md) introduces the IoT layer.
- [`iot/firmware/README.md`](iot/firmware/README.md) documents the ESP32
  firmware example.
- [`iot/logging/README.md`](iot/logging/README.md) documents telemetry logging.

## Contributing

1. Open or pick a GitHub issue that describes the work.
2. Branch from `main`, for example `git checkout -b fix/resource-validation`.
3. Keep changes aligned with the layered backend structure: `api`, `services`,
   `repositories`, `models`, and `schemas`.
4. Add or update tests for behavior changes.
5. Run `pytest backend/tests` before opening a pull request.
6. Document behavior changes in code docstrings or project docs.

## Dependency Note

`backend/requirements.txt` currently includes both runtime dependencies and test
tooling such as `pytest`, `pytest-asyncio`, and `httpx`. Production deployments
may eventually split these into separate runtime and development requirement
files.

## License

This repository does not currently include a root `LICENSE` file. Confirm the
intended project license before redistributing packaged builds.

## Maintainers

Muwanga Erasto Kosea, Ouma Ronald
