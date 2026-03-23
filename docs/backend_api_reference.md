# Backend API Reference

This guide documents the backend endpoints in `backend/app` and provides practical
request/response examples for local integration testing.

## Base URL and Interactive Docs

- Local base URL: `http://127.0.0.1:8000`
- OpenAPI JSON: `GET /openapi.json`
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

## Authentication

### Auth Endpoints (No Bearer Token Required)

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/auth/users` | Register a user |
| `POST` | `/api/v1/auth/token` | Obtain a bearer access token |

### Token Flow

1. Create user credentials.
2. Exchange credentials for a bearer token.
3. Send `Authorization: Bearer <token>` on protected routes.

```bash
# 1) Register user
curl -X POST "http://127.0.0.1:8000/api/v1/auth/users" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=apiuser&password=StrongPass123!"
```

Example response:

```json
{
  "username": "apiuser"
}
```

```bash
# 2) Login for token
curl -X POST "http://127.0.0.1:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=apiuser&password=StrongPass123!"
```

Example response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

```bash
# 3) Reuse token
export TOKEN="<jwt>"
```

### Protected Route Groups

These routers require bearer authentication:

- `/api/v1/projects`
- `/api/v1/resources`
- `/api/v1/locations`
- `/api/v1/maintenance-tickets`
- `/api/v1/sensor-sites`
- `/api/v1/alerts`

Public endpoints:

- `/health`
- `/api/v1/analytics/health`
- `/api/v1/auth/*`

## Common Conventions

### Pagination and Search

List endpoints for projects/resources/locations/tickets/sensor-sites accept:

- `limit` (integer, min `1`)
- `offset` (integer, min `0`)
- `search` (string)

Paginated response shape:

```json
{
  "data": [],
  "pagination": {
    "total": 0,
    "limit": 20,
    "offset": 0
  }
}
```

Search fields by entity:

| Entity | Search fields |
| --- | --- |
| Projects | `name`, `sponsor` |
| Resources | `name`, `category`, `serial_number` |
| Locations | `campus`, `building`, `room` |
| Maintenance Tickets | `reported_by`, `issue_summary` |
| Sensor Sites | `data_collection_endpoint` |

### Error Format

Service-level errors return JSON in this format:

```json
{
  "detail": "Human-readable message",
  "code": "RESOURCE_NOT_FOUND"
}
```

Common error codes:

- `RESOURCE_NOT_FOUND` (HTTP `404`)
- `VALIDATION_ERROR` (HTTP `400`)
- `SERVICE_ERROR` (HTTP `500`)

Auth failures may return HTTP `401` with:

```json
{
  "detail": "Could not validate credentials"
}
```

## Endpoint Catalog

### Health and Analytics

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | No | App health status |
| `GET` | `/api/v1/analytics/health` | No | Analytics service health status |

```bash
curl "http://127.0.0.1:8000/health"
```

```json
{
  "status": "ok"
}
```

### Projects

Enum values:

- `status`: `planned`, `in_progress`, `on_hold`, `completed`, `cancelled`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/projects` | Bearer | List projects |
| `GET` | `/api/v1/projects/{project_id}` | Bearer | Get project by ID |
| `POST` | `/api/v1/projects` | Bearer | Create project |
| `PUT` | `/api/v1/projects/{project_id}` | Bearer | Full replace project |
| `PATCH` | `/api/v1/projects/{project_id}` | Bearer | Partial update project |
| `DELETE` | `/api/v1/projects/{project_id}` | Bearer | Delete project |

Create request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Campus Network Upgrade",
    "description": "Upgrade backbone links for the main campus.",
    "status": "planned",
    "sponsor": "ICT Directorate",
    "start_date": "2026-03-23",
    "end_date": "2026-12-31",
    "primary_contact_email": "ict-directorate@example.edu"
  }'
```

Create response example (`201`):

```json
{
  "name": "Campus Network Upgrade",
  "description": "Upgrade backbone links for the main campus.",
  "status": "planned",
  "sponsor": "ICT Directorate",
  "start_date": "2026-03-23",
  "end_date": "2026-12-31",
  "primary_contact_email": "ict-directorate@example.edu",
  "id": 1
}
```

List example:

```bash
curl "http://127.0.0.1:8000/api/v1/projects?limit=5&offset=0&search=Campus" \
  -H "Authorization: Bearer $TOKEN"
```

### Resources

Enum values:

- `lifecycle_state`: `draft`, `active`, `maintenance`, `retired`

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/resources` | Bearer | List resources |
| `GET` | `/api/v1/resources/{resource_id}` | Bearer | Get resource by ID |
| `POST` | `/api/v1/resources` | Bearer | Create resource |
| `PUT` | `/api/v1/resources/{resource_id}` | Bearer | Full replace resource |
| `PATCH` | `/api/v1/resources/{resource_id}` | Bearer | Partial update resource |
| `DELETE` | `/api/v1/resources/{resource_id}` | Bearer | Delete resource |

Create request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/resources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Edge Sensor",
    "category": "sensor",
    "lifecycle_state": "active",
    "serial_number": "SN-001",
    "procurement_date": "2026-03-23",
    "description": "Outdoor air-quality node",
    "project_id": 1,
    "location_id": 1
  }'
```

Create response example (`201`):

```json
{
  "name": "Edge Sensor",
  "category": "sensor",
  "lifecycle_state": "active",
  "serial_number": "SN-001",
  "procurement_date": "2026-03-23",
  "description": "Outdoor air-quality node",
  "project_id": 1,
  "location_id": 1,
  "id": 1
}
```

Validation failure example (`400`):

```json
{
  "detail": "Project 9999 does not exist.",
  "code": "VALIDATION_ERROR"
}
```

### Locations

`geom` is optional and uses:

```json
{
  "lat": 0.3476,
  "lon": 32.5825
}
```

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/locations` | Bearer | List locations |
| `GET` | `/api/v1/locations/{location_id}` | Bearer | Get location by ID |
| `POST` | `/api/v1/locations` | Bearer | Create location |
| `PUT` | `/api/v1/locations/{location_id}` | Bearer | Full replace location |
| `PATCH` | `/api/v1/locations/{location_id}` | Bearer | Partial update location |
| `DELETE` | `/api/v1/locations/{location_id}` | Bearer | Delete location |

Create request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/locations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "campus": "Main Campus",
    "building": "Engineering Block",
    "room": "Lab 2",
    "geom": {"lat": 0.3476, "lon": 32.5825}
  }'
```

Create response example (`201`):

```json
{
  "campus": "Main Campus",
  "building": "Engineering Block",
  "room": "Lab 2",
  "geom": {"lat": 0.3476, "lon": 32.5825},
  "id": 1
}
```

### Maintenance Tickets

Enum values:

- `severity`: `low`, `medium`, `high`, `critical`
- `status`: `open`, `in_progress`, `resolved`, `closed`

Rule: when `status` is `resolved` or `closed`, both `closed_at` and `notes` are
required.

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/maintenance-tickets` | Bearer | List tickets |
| `GET` | `/api/v1/maintenance-tickets/{ticket_id}` | Bearer | Get ticket by ID |
| `POST` | `/api/v1/maintenance-tickets` | Bearer | Create ticket |
| `PUT` | `/api/v1/maintenance-tickets/{ticket_id}` | Bearer | Full replace ticket |
| `PATCH` | `/api/v1/maintenance-tickets/{ticket_id}` | Bearer | Partial update ticket |
| `DELETE` | `/api/v1/maintenance-tickets/{ticket_id}` | Bearer | Delete ticket |

Create request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/maintenance-tickets" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": 1,
    "reported_by": "helpdesk@example.edu",
    "issue_summary": "Device intermittently disconnects.",
    "severity": "high",
    "status": "open",
    "opened_at": "2026-03-23T09:00:00Z",
    "closed_at": null,
    "notes": null
  }'
```

Create response example (`201`):

```json
{
  "resource_id": 1,
  "reported_by": "helpdesk@example.edu",
  "issue_summary": "Device intermittently disconnects.",
  "severity": "high",
  "status": "open",
  "opened_at": "2026-03-23T09:00:00+00:00",
  "closed_at": null,
  "notes": null,
  "id": 1
}
```

### Sensor Sites

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/api/v1/sensor-sites` | Bearer | List sensor sites |
| `GET` | `/api/v1/sensor-sites/{site_id}` | Bearer | Get sensor site by ID |
| `POST` | `/api/v1/sensor-sites` | Bearer | Create sensor site |
| `PUT` | `/api/v1/sensor-sites/{site_id}` | Bearer | Full replace sensor site |
| `PATCH` | `/api/v1/sensor-sites/{site_id}` | Bearer | Partial update sensor site |
| `DELETE` | `/api/v1/sensor-sites/{site_id}` | Bearer | Delete sensor site |

Create request example:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/sensor-sites" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": 1,
    "project_id": 1,
    "location_id": 1,
    "data_collection_endpoint": "https://collector.example.edu/intake",
    "notes": "Roof-mounted sensor cluster"
  }'
```

Create response example (`201`):

```json
{
  "resource_id": 1,
  "project_id": 1,
  "location_id": 1,
  "data_collection_endpoint": "https://collector.example.edu/intake",
  "notes": "Roof-mounted sensor cluster",
  "id": 1
}
```

### Alerts

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `POST` | `/api/v1/alerts` | Bearer | Create an alert when value breaches threshold |
| `GET` | `/api/v1/alerts/{sensor_id}` | Bearer | List alerts for a sensor site |

`POST /api/v1/alerts` uses query parameters (`sensor_id`, `metric`, `value`,
`threshold`).

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/alerts?sensor_id=1&metric=temperature&value=48.5&threshold=40.0" \
  -H "Authorization: Bearer $TOKEN"
```

Example response when threshold is exceeded:

If `value <= threshold`, the endpoint returns `null`.

```json
{
  "id": 7,
  "sensor_id": 1,
  "metric": "temperature",
  "value": 48.5,
  "threshold": 40.0,
  "timestamp": "2026-03-23T09:10:00"
}
```

Get alerts by sensor:

```bash
curl "http://127.0.0.1:8000/api/v1/alerts/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Quick End-to-End Test Sequence

Use this order for local smoke testing:

1. `POST /api/v1/auth/users`
2. `POST /api/v1/auth/token`
3. `POST /api/v1/projects`
4. `POST /api/v1/locations`
5. `POST /api/v1/resources`
6. `POST /api/v1/sensor-sites`
7. `POST /api/v1/maintenance-tickets`
8. `GET` list endpoints with `limit`, `offset`, and `search`
9. `PATCH` and `DELETE` on created IDs
