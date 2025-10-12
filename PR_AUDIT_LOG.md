# 🔍 Feature: Audit Log & Activity Tracking

## 📌 Issue Reference

- Addresses **Issue #6 – Audit Log / Activity Tracking**

## 🧭 What’s Included

- Introduced `AuditLog` ORM model, Pydantic schemas, repository, and Alembic migration.
- Added `AuditLogService`, `AuditTrailRecorder`, and FastAPI router at `/api/v1/audit-logs` with list/read/create endpoints.
- Wired audit hooks into project, resource, maintenance-ticket, and document services using authenticated actor context.
- Enriched document service with download access logging and ensured API routers pass `current_user` metadata.
- Extended test infrastructure to support GeoAlchemy on SQLite and added targeted service/API regression tests.
- Authenticated helpers and documentation (`backend/AUDIT_LOGGING.md`) outlining usage, design, and testing strategy.

## ✅ Testing

- `python3 -m pytest tests/services/test_audit_log_service.py -q`
- `python3 -m pytest tests/api/test_audit_logs.py -q`
- `python3 -m pytest tests/services/test_project_service_audit.py -q`

## 📝 Notes for Reviewers

- GeoAlchemy2 callbacks are disabled in tests (see `tests/conftest.py`) so SQLite in-memory databases work without SpatiaLite.
- API routers now require `current_user` in request handlers to capture actor information—existing overrides were updated accordingly.
