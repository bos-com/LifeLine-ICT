"""
Application configuration helpers.

Configuration is centralised through a ``Settings`` dataclass so that the
backend can be tuned using environment variables without touching source code.
The defaults reflect a development setup appropriate for lab machines and ICT
clubs, while production deployments can override the values through exported
variables or a ``.env`` file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _int_from_env(var_name: str, default: int) -> int:
    """Read an integer from the environment, falling back to ``default``."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


def _csv_from_env(var_name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    """Read a comma-separated string list from the environment."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return default

    values = tuple(value.strip() for value in raw_value.split(",") if value.strip())
    return values or default


@dataclass
class Settings:
    """
    Capture environment-driven configuration for the backend service.

    Attributes
    ----------
    database_url:
        SQLAlchemy connection string. The default uses SQLite with the async
        driver for portability, ideal for quick campus demonstrations.
    api_version:
        Semantic version surfaced via the OpenAPI schema.
    contact_email:
        Primary contact published in API metadata to support stakeholder
        communication and help-desk routing.
    pagination_default_limit:
        Default number of records returned by list endpoints. The value aligns
        with UX recommendations for screen reader users.
    pagination_max_limit:
        Safety guard to prevent accidental data dumps that could strain shared
        infrastructure.
    cors_allowed_origins:
        Browser origins allowed to call the API. Production deployments should
        configure this explicitly for their frontend domains.
    cors_allow_credentials:
        Whether browsers may include credentials on cross-origin requests.
    """

    database_url: str = os.getenv(
        "LIFELINE_DATABASE_URL",
        "sqlite+aiosqlite:///./lifeline.db",
    )
    api_version: str = os.getenv("LIFELINE_API_VERSION", "0.1.0")
    contact_email: str = os.getenv(
        "LIFELINE_CONTACT_EMAIL",
        "ict-support@lifeline.example.edu",
    )
    pagination_default_limit: int = _int_from_env(
        "LIFELINE_PAGINATION_DEFAULT_LIMIT",
        20,
    )
    pagination_max_limit: int = _int_from_env(
        "LIFELINE_PAGINATION_MAX_LIMIT",
        100,
    )
    cors_allowed_origins: tuple[str, ...] = _csv_from_env(
        "LIFELINE_CORS_ALLOWED_ORIGINS",
        (
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ),
    )
    cors_allow_credentials: bool = os.getenv(
        "LIFELINE_CORS_ALLOW_CREDENTIALS",
        "true",
    ).lower() in {"1", "true", "yes", "on"}


settings = Settings()
