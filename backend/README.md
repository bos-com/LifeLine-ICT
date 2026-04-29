# LifeLine-ICT Backend Setup

This guide focuses on the FastAPI backend located in `backend/`.

## Prerequisites

- Python 3.11+
- `pip`
- Optional: a virtual environment tool such as `venv`

## Local Setup

From the `backend/` directory:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux or macOS
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the sample configuration before running the app:

```bash
cp .env.example .env
```

If you are using PowerShell on Windows, the equivalent command is:

```powershell
Copy-Item .env.example .env
```

### Key Settings

- `LIFELINE_DATABASE_URL`: async database URL used by SQLAlchemy
- `LIFELINE_API_VERSION`: version shown in the FastAPI docs
- `LIFELINE_CONTACT_EMAIL`: support contact displayed in OpenAPI metadata
- `LIFELINE_PAGINATION_DEFAULT_LIMIT`: default list size for collection endpoints
- `LIFELINE_PAGINATION_MAX_LIMIT`: upper bound accepted by pagination params

The default sample config uses local SQLite, which is enough for first-time
setup and classroom development.

## Database Migrations

Run migrations from the `backend/` directory:

```bash
alembic upgrade head
```

Create a new migration when models change:

```bash
alembic revision --autogenerate -m "describe_change"
```

## Running the API

If you are inside `backend/`, start the development server with:

```bash
uvicorn app.main:app --reload
```

Useful endpoints after startup:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- App health: `http://127.0.0.1:8000/health`

## Running Tests

From the repository root:

```bash
pytest backend/tests
```

If you are already inside `backend/`, run:

```bash
pytest tests
```

## Optional Seed Data

Populate sample data for demos or manual testing:

```bash
python scripts/seed_sample_data.py
```
