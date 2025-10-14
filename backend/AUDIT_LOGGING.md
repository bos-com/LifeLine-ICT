## Audit Logging Module

The audit logging module provides immutable activity tracking across the
LifeLine-ICT backend. It captures who performed an action, what entity was
affected, and contextual metadata that supports compliance reviews.

### Data Model

- **Table**: `audit_logs`
- **Key fields**:
  - `action` (`create`, `update`, `delete`, `access`, `status_change`, `attachment`)
  - `entity_type` (`project`, `resource`, `maintenance_ticket`, `document`, …)
  - `entity_id` (text ID of the affected entity)
  - `actor_type` (`user`, `system`, `service`, `admin`)
  - `actor_id` / `actor_name` (optional identifiers for actors)
  - `summary` / `description`
  - `context` (JSON metadata such as field deltas)
  - Timestamps inherited from `TimestampMixin`

Indexes are provided on `created_at`, `action`, and `(entity_type, entity_id)`
to support dashboard queries.

### Service Layer

`AuditLogService` exposes convenience methods:

```python
service = AuditLogService(session)
await service.record_event(AuditLogCreate(...))
await service.list_logs(AuditLogQuery(limit=20))
await service.get_log(log_id)
```

The helper `AuditTrailRecorder` wraps the service with sensible defaults for a
given entity type and automatically serialises context payloads.

### API Endpoints

Registered under `/api/v1/audit-logs`:

| Method | Path                 | Description                     |
|--------|---------------------|---------------------------------|
| GET    | `/`                 | Paginated listing with filters  |
| GET    | `/{log_id}`         | Fetch a single log entry        |
| POST   | `/`                 | Append a new audit event        |

Endpoints require authentication (`get_current_user`) and reuse the shared
pagination scheme (`limit`, `offset`, `search`, plus audit-specific filters).

### Automatic Hooks

Key services now emit audit entries after successful operations:

- Projects: create, update, delete
- ICT Resources: create, update, delete
- Maintenance Tickets: create, update, delete
- Document management: upload, metadata update, delete, download

Routers pass the authenticated user to ensure actor details are recorded.

### Testing

- `tests/services/test_audit_log_service.py` verifies persistence and filter
  behaviour.
- `tests/api/test_audit_logs.py` exercises the REST endpoints.
- `tests/services/test_project_service_audit.py` confirms service hooks emit logs.

When running the test suite on SQLite, geometry columns are compiled as `BLOB`
and GeoAlchemySpatial callbacks are disabled (see `tests/conftest.py`), allowing
the audit tests to execute without SpatiaLite.
