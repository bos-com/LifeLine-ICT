"""
Application configuration helpers.

Configuration is centralised through a `Settings` object so that the backend
can be tuned using environment variables without touching source code. The
defaults reflect a development setup appropriate for lab machines and ICT
clubs, while production deployments can override the values through exported
variables or a `.env` file.
"""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
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
    """

    database_url: str = Field(
        default="sqlite+aiosqlite:///./lifeline.db",
        description=(
            "SQLAlchemy DSN for the primary database. Uses async SQLite by "
            "default for developer convenience."
        ),
    )
    api_version: str = Field(
        default="0.1.0",
        description="Version identifier surfaced in the generated OpenAPI spec.",
    )
    contact_email: str = Field(
        default="ict-support@lifeline.example.edu",
        description=(
            "Point of contact for API consumers. Update to an institutional "
            "mailbox during deployment."
        ),
    )
    pagination_default_limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Default number of items returned by list endpoints.",
    )
    pagination_max_limit: int = Field(
        default=100,
        ge=10,
        description="Upper bound for list endpoint page sizes.",
    )

    class Config:
        """Pydantic configuration for environment loading."""

        env_file = ".env"
        env_prefix = "LIFELINE_"


settings = Settings()
