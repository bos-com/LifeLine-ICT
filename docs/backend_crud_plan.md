# Backend CRUD API Implementation Plan

## Context

Issue `#5` calls for fully fledged CRUD APIs that expose the primary information systems for the LifeLine-ICT initiative. The backend needs to complement the existing IoT ingestion layer (`iot/logging/log_data.py`) while preparing for future integrations such as authentication, analytics, and audit logging. The APIs will support university administrators, ICT support teams, and researchers who rely on accurate digital asset information and project status data.

## Design Principles

1. **Clarity and Maintainability** – Favour explicit module boundaries (`api`, `services`, `repositories`, `models`, `schemas`) with docstrings that spell out institutional usage scenarios.
2. **Separation of Concerns** – Use a layered architecture so persistence changes do not cascade into presentation logic.
3. **Extensibility** – Opt for FastAPI and SQLAlchemy to take advantage of their async capabilities and OpenAPI generation for future integration with frontend dashboards.
4. **Testability** – Provide deterministic fixtures and service-level tests to safeguard business rules.
5. **Operational Awareness** – Embed structured logging hooks so that downstream monitoring and audit modules (issues `#6` and `#7`) can piggyback on the same pipeline.

## Target Entities

| Entity | Purpose | Key Fields |
| --- | --- | --- |
| `Project` | Tracks ICT initiatives, grants, and deployments | `id`, `name`, `description`, `status`, `sponsor`, `start_date`, `end_date`, `primary_contact_email` |
| `ICTResource` | Represents hardware, software, or service assets | `id`, `name`, `category`, `lifecycle_state`, `serial_number`, `procurement_date`, `project_id`, `location_id` |
| `Location` | Captures campus/site information for assets and sensors | `id`, `campus`, `building`, `room`, `latitude`, `longitude` |
| `MaintenanceTicket` | Records support interventions and escalations | `id`, `resource_id`, `reported_by`, `issue_summary`, `severity`, `status`, `opened_at`, `closed_at`, `notes` |
| `SensorSite` | Maps IoT deployment sites to resources and projects | `id`, `resource_id`, `project_id`, `data_collection_endpoint`, `notes` |

## API Surface

For every entity the API will expose:

* `GET /api/v1/<entity>` – List with pagination (`limit`, `offset`) and keyword filtering via query parameters.
* `GET /api/v1/<entity>/{id}` – Retrieve a single record with contextual links (e.g., related tickets for a resource).
* `POST /api/v1/<entity>` – Create a new record with validation of foreign keys and enumerations.
* `PUT /api/v1/<entity>/{id}` – Replace an existing record.
* `PATCH /api/v1/<entity>/{id}` – Partial update using schema with optional fields.
* `DELETE /api/v1/<entity>/{id}` – Soft delete (status flip) where business rules allow, otherwise hard delete.

Error responses will include machine-readable codes (e.g., `RESOURCE_NOT_FOUND`, `VALIDATION_ERROR`) to streamline frontend handling.

## Layered Architecture

```
backend/
├── app/
│   ├── api/           # FastAPI routers and dependency injection
│   ├── core/          # Config, logging, database session management
│   ├── models/        # SQLAlchemy ORM models
│   ├── repositories/  # Data access abstractions
│   ├── schemas/       # Pydantic models for requests/responses
│   └── services/      # Business rules and orchestration logic
└── tests/
    ├── api/
    ├── repositories/
    └── services/
```

`core/database.py` will expose a session factory using SQLAlchemy’s async engine. Configuration values (database URL, pagination defaults) will load from environment variables with `.env` support.

## Pagination & Filtering

* Default page size: 20 results (configurable).
* Maximum page size: 100 results to avoid expensive queries.
* Filtering will allow case-insensitive search on key string fields (`name`, `status`, `campus`, etc.).
* Sorting hooks will be added in a follow-up once analytics needs (issue `#3`) are clarified.

## Testing Strategy

* Use `pytest` with `anyio` for async tests.
* In-memory SQLite database per test module with automatic schema creation.
* Factories to generate sample entities for relationship coverage.
* Coverage focus:
  * Repository CRUD operations including constraint violations.
  * Service-level invariants (e.g., cannot close a maintenance ticket without resolution notes).
  * API endpoints for happy path, validation failures, pagination boundaries.

## Documentation & Tooling

* Generate OpenAPI schema via FastAPI’s `/docs` and `/openapi.json`.
* Update the root `README.md` with backend setup steps, environment configuration, and curl examples.
* Provide a `Makefile` (target `make backend-dev`) in a follow-up issue for developer convenience.

## Milestones & Commit Breakdown

1. Introduce this architectural plan.
2. Scaffold the backend application skeleton and dependencies.
3. Define ORM models with verbose docstrings.
4. Add Pydantic schemas and validation metadata.
5. Implement repositories with pagination helpers.
6. Implement service layer with business rules and logging hooks.
7. Wire up API routers and global error handlers.
8. Cover critical paths with tests.
9. Document setup and usage in `README.md`.
10. Polish developer tooling (e.g., local `.env.example`, sample curl script).

This plan keeps issue `#5` deliverables at the forefront while creating a sustainable foundation for the broader LifeLine-ICT platform.
