# Backend Setup Guide

This guide covers setting up the LifeLine-ICT FastAPI backend locally.

## Prerequisites

- Python 3.11+
- pip

## Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn backend.app.main:app --reload
```

API available at: `http://127.0.0.1:8000`
Swagger docs at: `http://127.0.0.1:8000/docs`

## Database Migrations

```bash
alembic upgrade head
```

## Running Tests

```bash
pytest backend/tests
```

## API Endpoints

| Method | Endpoint                        | Description                  |
|--------|---------------------------------|------------------------------|
| GET    | /api/v1/projects                | List all ICT projects        |
| POST   | /api/v1/projects                | Create a new project         |
| GET    | /api/v1/projects/{id}           | Get project by ID            |
| PUT    | /api/v1/projects/{id}           | Update a project             |
| DELETE | /api/v1/projects/{id}           | Delete a project             |
| GET    | /api/v1/resources               | List all ICT resources       |
| POST   | /api/v1/resources               | Create a new resource        |
| GET    | /api/v1/locations               | List all locations           |
| POST   | /api/v1/locations               | Create a location            |
| GET    | /api/v1/maintenance-tickets     | List maintenance tickets     |
| POST   | /api/v1/maintenance-tickets     | Create a maintenance ticket  |
| GET    | /api/v1/sensor-sites            | List IoT sensor sites        |
| POST   | /api/v1/sensor-sites            | Create a sensor site         |

## Business Rules

- A resource **cannot be deleted** while it has open maintenance tickets
- Closing a ticket **requires** a resolution note
- Sensor sites must be linked to an existing resource and location