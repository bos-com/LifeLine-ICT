# LifeLine-ICT API Reference

This document is the centralized reference for the currently implemented
backend routes. It complements the live FastAPI docs at
`http://127.0.0.1:8000/docs`.

## Base URLs

- Local API root: `http://127.0.0.1:8000`
- Versioned API prefix: `http://127.0.0.1:8000/api/v1`

## Authentication

### Create a user

`POST /api/v1/auth/users`

The auth routes use `OAuth2PasswordRequestForm`, so credentials are sent as form
fields rather than JSON.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/users \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo-admin&password=change-me"
```

### Obtain a bearer token

`POST /api/v1/auth/token`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo-admin&password=change-me"
```

Example response:

```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

### Protected routes

The CRUD routers are wired with a bearer-token dependency. Send the token using:

```text
Authorization: Bearer <access_token>
```

Role-based restrictions are not yet implemented in the current source tree, so
the present auth model is authenticated-user access rather than role-scoped
access.

## Shared Query Parameters

Collection endpoints accept these optional query parameters:

| Parameter | Description |
| --- | --- |
| `limit` | Number of records to return |
| `offset` | Zero-based starting position |
| `search` | Case-insensitive free-text filter |

Paginated responses use this envelope:

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

## Health and Utility Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Application availability check |
| `GET` | `/api/v1/analytics/health` | Lightweight analytics module health check |

## Projects

| Method | Path |
| --- | --- |
| `GET` | `/api/v1/projects` |
| `GET` | `/api/v1/projects/{project_id}` |
| `POST` | `/api/v1/projects` |
| `PUT` | `/api/v1/projects/{project_id}` |
| `PATCH` | `/api/v1/projects/{project_id}` |
| `DELETE` | `/api/v1/projects/{project_id}` |

Example create payload:

```json
{
  "name": "Campus Network Upgrade",
  "description": "Upgrade backbone links for the main campus.",
  "status": "planned",
  "sponsor": "ICT Directorate",
  "start_date": "2026-04-29",
  "end_date": "2026-08-29",
  "primary_contact_email": "ict-directorate@example.edu"
}
```

Example response:

```json
{
  "id": 1,
  "name": "Campus Network Upgrade",
  "description": "Upgrade backbone links for the main campus.",
  "status": "planned",
  "sponsor": "ICT Directorate",
  "start_date": "2026-04-29",
  "end_date": "2026-08-29",
  "primary_contact_email": "ict-directorate@example.edu"
}
```

## ICT Resources

| Method | Path |
| --- | --- |
| `GET` | `/api/v1/resources` |
| `GET` | `/api/v1/resources/{resource_id}` |
| `POST` | `/api/v1/resources` |
| `PUT` | `/api/v1/resources/{resource_id}` |
| `PATCH` | `/api/v1/resources/{resource_id}` |
| `DELETE` | `/api/v1/resources/{resource_id}` |

Required fields for create and full update:

- `name`
- `category`
- `lifecycle_state`

Optional linkage fields:

- `project_id`
- `location_id`

## Locations

| Method | Path |
| --- | --- |
| `GET` | `/api/v1/locations` |
| `GET` | `/api/v1/locations/{location_id}` |
| `POST` | `/api/v1/locations` |
| `PUT` | `/api/v1/locations/{location_id}` |
| `PATCH` | `/api/v1/locations/{location_id}` |
| `DELETE` | `/api/v1/locations/{location_id}` |

Example geometry payload:

```json
{
  "campus": "Main Campus",
  "building": "ICT Block",
  "room": "Lab 2",
  "geom": {
    "lat": 0.3476,
    "lon": 32.5825
  }
}
```

## Maintenance Tickets

| Method | Path |
| --- | --- |
| `GET` | `/api/v1/maintenance-tickets` |
| `GET` | `/api/v1/maintenance-tickets/{ticket_id}` |
| `POST` | `/api/v1/maintenance-tickets` |
| `PUT` | `/api/v1/maintenance-tickets/{ticket_id}` |
| `PATCH` | `/api/v1/maintenance-tickets/{ticket_id}` |
| `DELETE` | `/api/v1/maintenance-tickets/{ticket_id}` |

Important fields:

- `resource_id`
- `reported_by`
- `issue_summary`
- `severity`
- `status`
- `opened_at`

## Sensor Sites

| Method | Path |
| --- | --- |
| `GET` | `/api/v1/sensor-sites` |
| `GET` | `/api/v1/sensor-sites/{site_id}` |
| `POST` | `/api/v1/sensor-sites` |
| `PUT` | `/api/v1/sensor-sites/{site_id}` |
| `PATCH` | `/api/v1/sensor-sites/{site_id}` |
| `DELETE` | `/api/v1/sensor-sites/{site_id}` |

Required fields:

- `resource_id`
- `data_collection_endpoint`

Optional fields:

- `project_id`
- `location_id`
- `notes`

## Alerts

| Method | Path | Notes |
| --- | --- | --- |
| `POST` | `/api/v1/alerts` | Parameters are currently accepted as query parameters |
| `GET` | `/api/v1/alerts/{sensor_id}` | Returns alerts for one sensor |

Example alert creation request:

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/alerts?sensor_id=3&metric=temperature&value=38.4&threshold=35.0" \
  -H "Authorization: Bearer <access_token>"
```

## Common Error Responses

- `401 Unauthorized`: Missing or invalid bearer token
- `404 Not Found`: Requested record does not exist
- `422 Unprocessable Entity`: Validation failed for the submitted payload
