# Backend Setup Guide (.env and Local Run)

This guide explains how to configure and run the backend service consistently.

## 1. Prerequisites

- Python 3.11+
- `pip`
- Access to project repository

## 2. Create and Activate Virtual Environment

```bash
python -m venv .venv

# macOS/Linux/Git Bash
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\activate
```

## 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file in the backend runtime context and define required values.
Use safe defaults for local development and never commit production secrets.

Recommended minimum variables:

```env
ENV=development
DEBUG=true
DATABASE_URL=sqlite:///./lifeline.db
SECRET_KEY=change-me-in-real-environments
```

If your deployment uses different settings (PostgreSQL, external services), override these values accordingly.

## 5. Run API

```bash
uvicorn backend.app.main:app --reload
```

## 6. Verify Setup

1. Open API docs at `http://127.0.0.1:8000/docs`
2. Call a basic endpoint to confirm service health.
3. Run tests:

```bash
pytest backend/tests
```

## 7. Common Pitfalls

- Missing virtual environment activation
- Missing/incorrect `.env` values
- Dependency version drift between environments

Use this checklist before opening pull requests that affect backend behavior.
