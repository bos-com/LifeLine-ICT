# Plan for Implementing Real-Time Alert Engine

This plan outlines the steps to implement the real-time alert engine for the LifeLine-ICT project, as described in GitHub Issue #3.

**Status: Implemented**

## 1. Create the `alert_engine` Module

- Create a new directory `backend/app/alert_engine`.
- This module will contain the logic for the real-time alert engine.

## 2. Implement the `Alert` Model

- Create a new file `backend/app/models/alert.py`.
- This model will represent an alert in the database, including fields for `sensor_id`, `metric`, `value`, `threshold`, and `timestamp`.

## 3. Implement the `AlertRepository`

- Create a new file `backend/app/repositories/alert_repository.py`.
- This repository will handle the database operations for the `Alert` model, including creating and retrieving alerts.

## 4. Implement the `AlertService`

- Create a new file `backend/app/services/alert_service.py`.
- This service will contain the business logic for creating and retrieving alerts, including checking for threshold breaches.

## 5. Implement the `alert_router`

- Create a new file `backend/app/api/alert_router.py`.
- This router will expose the alert endpoints to the API, including an endpoint for creating alerts and an endpoint for retrieving alerts.

## 6. Integrate the `alert_router` into the Main Application

- In `backend/app/main.py`, import and include the `alert_router`.
- This will make the alert endpoints available to users.

## 7. Add Unit Tests for the `alert_engine` Module

- Create a new file `backend/tests/alert_engine/test_alert_service.py`.
- Add unit tests to ensure that the alert engine is working correctly, including testing the threshold breach logic.

## 8. Create a CI Pipeline

- Create a new file `.github/workflows/ci.yml`.
- This pipeline will automate the testing of the application on every push to the repository.

# Plan for Implementing Audit Log / Activity Tracking (Issue #6)

**Status: Implemented**

## 1. Establish Audit Logging Foundations

- Define the `AuditLog` ORM model with action/entity enumerations and structured metadata (actor, context, source).
- Create matching Pydantic schemas to validate API requests and shape responses.
- Produce an Alembic migration to create the `audit_logs` table with efficient indexes.

## 2. Build Repository & Service Layer

- Implement `AuditLogRepository` to persist entries and support filtered queries (action, entity, actor, date).
- Introduce an `AuditLogService` with helper methods to record events and bundle pagination logic.
- Add integration hooks to core services (projects, resources, maintenance tickets, documents) to capture key lifecycle actions.

## 3. Expose Audit Log API Endpoints

- Create a FastAPI router under `/api/v1/audit-logs` with endpoints to list and inspect audit history.
- Support pagination, filtering, and keyword search to help compliance reviews.
- Ensure responses include contextual metadata for downstream dashboards.

## 4. Testing Strategy

- Add targeted unit tests for the repository/service to verify filtering, persistence, and validation rules.
- Expand API tests to cover listing, filtering, and empty-state responses.
- Provide fixtures/mocks to simulate service hooks without relying on external dependencies.

## 5. Documentation & Developer Experience

- Document usage patterns in a dedicated `AUDIT_LOGGING.md` guide outlining data model and integration hooks.
- Update inline docstrings across new modules to maintain the project's documentation standard.
- Prepare `PR_AUDIT_LOG.md` summarising implementation details for maintainers.
