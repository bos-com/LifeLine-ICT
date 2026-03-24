"""Repository for project entities."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Project
from .base import AsyncRepository


class ProjectRepository(AsyncRepository[Project]):
    """Persist and query project entities."""

    searchable_fields = (Project.name, Project.sponsor)

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)
