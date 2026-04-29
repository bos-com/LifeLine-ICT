# API Documentation

## Overview
This document describes all REST API endpoints for LifeLine-ICT.

## Base URL
```
https://api.lifeline-ict.org/v1
```

## Authentication
Most endpoints require API key in header:
```
X-API-Key: your-api-key
```

## Endpoints

### Patients

#### GET /patients
List all patients.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "PAT-001",
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

#### GET /patients/:id
Get a single patient by ID.

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "PAT-001",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  }
}
```

#### POST /patients
Create a new patient.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "PAT-001",
    "name": "John Doe"
  }
}
```

#### PUT /patients/:id
Update an existing patient.

**Request Body:**
```json
{
  "name": "John Smith",
  "phone": "+1987654321"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Patient updated successfully"
}
```

#### DELETE /patients/:id
Delete a patient.

**Response:**
```json
{
  "status": "success",
  "message": "Patient deleted successfully"
}
```

### Incidents

#### GET /incidents
List all incidents.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "INC-001",
      "type": "emergency",
      "location": "Downtown",
      "status": "active"
    }
  ]
}
```

#### POST /incidents
Report a new incident.

**Request Body:**
```json
{
  "type": "emergency",
  "location": "Downtown",
  "description": "Medical emergency"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 500 | Internal Server Error |

## Rate Limiting
- 100 requests per minute per API key
- 1000 requests per hour per API key

## Version History
| Version | Date | Changes |
|---------|------|---------|
| v1.0.0 | 2026-01-01 | Initial release |
