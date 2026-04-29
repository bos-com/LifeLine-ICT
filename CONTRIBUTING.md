# Contributing to LifeLine-ICT

LifeLine-ICT spans backend APIs, IoT examples, and operations documentation.
Focused contributions help maintainers review changes safely.

## Before You Start

1. Search GitHub Issues for an existing bug, enhancement, or documentation task.
2. Open a new issue when the work is not already tracked.
3. Keep pull requests scoped to one clear improvement.

## Branching and Commits

Use a descriptive branch name:

```bash
git checkout -b fix/resource-ticket-validation
git checkout -b docs/iot-logging-guide
```

Use conventional commit prefixes such as `fix:`, `feat:`, `docs:`, and
`style:`.

## Backend Changes

- Keep request handling in `backend/app/api`.
- Put business rules in `backend/app/services`.
- Keep persistence behavior in `backend/app/repositories`.
- Update Pydantic schemas when API payloads change.
- Add or update tests under `backend/tests`.

Run:

```bash
pytest backend/tests
```

## IoT Changes

- Document hardware assumptions and sensor wiring changes.
- Keep telemetry field names stable unless the backend or docs are updated at
  the same time.
- Avoid committing real deployment credentials, device IDs, or campus network
  secrets.

## Pull Request Checklist

- The PR links the issue it resolves.
- The change is focused and reviewable.
- Backend behavior changes include tests.
- Documentation is updated for setup, API, firmware, or operations changes.
- No real credentials, private network details, or production telemetry samples
  are included.
