# LifeLine-ICT API Reference

This document covers all backend API endpoints exposed by the LifeLine-ICT FastAPI service. The API manages ICT projects, resources, locations, maintenance tickets, and IoT sensor sites for the Uganda University ICT infrastructure platform.

**Base URL:** `http://127.0.0.1:8000`
**Interactive docs:** `http://127.0.0.1:8000/docs` (Swagger UI)
**OpenAPI schema:** `http://127.0.0.1:8000/openapi.json`

All list endpoints support `limit`, `offset`, and `search` query parameters and return pagination metadata.

---

##  Projects

Projects represent strategic ICT initiatives. Resources and sensor sites are grouped under projects.

### `GET /api/v1/projects`

Returns a paginated list of all ICT projects.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Max results to return |
| `offset` | integer | 0 | Number of results to skip |
| `search` | string | — | Filter by project name or description |

**Example Request:**
**Example Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Campus Network Upgrade 2026",
      "description": "Upgrading fibre backbone across all faculties",
      "status": "active",
      "created_at": "2026-01-15T08:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10,
  "offset": 0
}
```

### `POST /api/v1/projects`

Creates a new ICT project.

**Request Body:**
```json
{
  "name": "Campus Network Upgrade 2026",
  "description": "Upgrading fibre backbone across all faculties",
  "status": "active"
}
```

### `GET /api/v1/projects/{id}`

Returns a single project by ID.

### `PUT /api/v1/projects/{id}`

Updates an existing project.

### `DELETE /api/v1/projects/{id}`

Deletes a project. Will fail if resources are still linked to it.

---

##  ICT Resources

Resources are physical or digital assets (servers, routers, computers) tracked within the system.

### `GET /api/v1/resources`

Returns a paginated list of ICT resources.

**Query Parameters:** `limit`, `offset`, `search`, `project_id`, `location_id`

**Example Request:**
**Example Response:**
```json
{
  "items": [
    {
      "id": 12,
      "name": "Core Router A",
      "type": "networking",
      "status": "operational",
      "project_id": 1,
      "location_id": 3,
      "created_at": "2026-02-01T09:00:00Z"
    }
  ],
  "total": 1,
  "limit": 5,
  "offset": 0
}
```

### `POST /api/v1/resources`

Creates a new resource. `project_id` and `location_id` must reference existing records.

**Request Body:**
```json
{
  "name": "Core Router A",
  "type": "networking",
  "status": "operational",
  "project_id": 1,
  "location_id": 3
}
```

### `GET /api/v1/resources/{id}`
### `PUT /api/v1/resources/{id}`
### `DELETE /api/v1/resources/{id}`

>  **Note:** A resource cannot be deleted while it has open maintenance tickets. Close or resolve all tickets first.

---

##  Locations

Locations represent physical places on campus where resources or sensor nodes are deployed.

### `GET /api/v1/locations`

Returns a paginated list of locations with geographic metadata.

**Example Response:**
```json
{
  "items": [
    {
      "id": 3,
      "name": "Faculty of Science Server Room",
      "building": "Science Block",
      "latitude": 0.4316,
      "longitude": 32.4445,
      "created_at": "2026-01-10T07:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### `POST /api/v1/locations`

**Request Body:**
```json
{
  "name": "Faculty of Science Server Room",
  "building": "Science Block",
  "latitude": 0.4316,
  "longitude": 32.4445
}
```

### `GET /api/v1/locations/{id}`
### `PUT /api/v1/locations/{id}`
### `DELETE /api/v1/locations/{id}`

---

##  Maintenance Tickets

Tickets track faults, repairs, and scheduled maintenance for ICT resources.

### `GET /api/v1/maintenance-tickets`

Returns paginated maintenance tickets. Filter by resource or status.

**Query Parameters:** `limit`, `offset`, `search`, `resource_id`, `status`

**Example Request:****Example Response:**
```json
{
  "items": [
    {
      "id": 7,
      "resource_id": 12,
      "title": "Router intermittent packet loss",
      "description": "Core Router A dropping ~5% of packets since 2026-04-01",
      "status": "open",
      "resolution_notes": null,
      "created_at": "2026-04-01T11:00:00Z",
      "resolved_at": null
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### `POST /api/v1/maintenance-tickets`

**Request Body:**
```json
{
  "resource_id": 12,
  "title": "Router intermittent packet loss",
  "description": "Core Router A dropping ~5% of packets since 2026-04-01",
  "status": "open"
}
```

### `PUT /api/v1/maintenance-tickets/{id}`

To **close** a ticket, set `status` to `resolved` and include `resolution_notes`. The API will reject a close request without resolution notes.

**Request Body (closing a ticket):**
```json
{
  "status": "resolved",
  "resolution_notes": "Replaced faulty SFP module. Packet loss resolved as of 2026-04-03."
}
```

### `GET /api/v1/maintenance-tickets/{id}`
### `DELETE /api/v1/maintenance-tickets/{id}`

---

##  Sensor Sites

Sensor sites link IoT deployments to resources, projects, and locations in the data model.

### `GET /api/v1/sensor-sites`

Returns paginated sensor sites.

**Query Parameters:** `limit`, `offset`, `search`, `resource_id`, `project_id`, `location_id`

**Example Response:**
```json
{
  "items": [
    {
      "id": 2,
      "name": "North Campus Flood Sensor",
      "device_id": "node-001",
      "resource_id": 12,
      "project_id": 1,
      "location_id": 3,
      "status": "active",
      "created_at": "2026-03-01T06:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### `POST /api/v1/sensor-sites`

**Request Body:**
```json
{
  "name": "North Campus Flood Sensor",
  "device_id": "node-001",
  "resource_id": 12,
  "project_id": 1,
  "location_id": 3,
  "status": "active"
}
```

### `GET /api/v1/sensor-sites/{id}`
### `PUT /api/v1/sensor-sites/{id}`
### `DELETE /api/v1/sensor-sites/{id}`

---

##  Error Responses

All endpoints return standard error responses:

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad request — invalid input data |
| `404` | Resource not found |
| `422` | Validation error — check request body fields |
| `500` | Internal server error |

**Example 422 Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

##  Running the API Locally

```bash
# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Start the server
uvicorn backend.app.main:app --reload

# Run tests
pytest backend/tests
```

For IoT sensor setup, see [iot-setup-guide.md](iot-setup-guide.md).
