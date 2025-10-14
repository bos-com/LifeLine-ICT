"""
Generic repository helpers wrapping SQLAlchemy operations.

Repositories keep database access logic reusable and make unit tests easier to
write by isolating SQLAlchemy usage in a single layer.
"""

from __future__ import annotations

from typing import Any, Dict, Generic, Optional, Sequence, Tuple, Type, TypeVar

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

from ..core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class AsyncRepository(Generic[ModelType]):
    """
    Provide CRUD helpers for SQLAlchemy models.

    Parameters
    ----------
    session:
        SQLAlchemy async session supplied by the API layer.
    model:
        ORM model class managed by the repository.
    searchable_fields:
        Iterable of column attributes used for free-text search.
    """

    searchable_fields: Tuple[ColumnElement[str], ...] = ()

    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    def _base_select(self) -> Select[tuple[ModelType]]:
        """Return a base select statement for the model."""

        return select(self.model)

    def _apply_search(
        self,
        stmt: Select[tuple[ModelType]],
        search: Optional[str],
    ) -> Select[tuple[ModelType]]:
        """
        Apply case-insensitive LIKE filters across configured search fields.
        """

        if not search or not self.searchable_fields:
            return stmt

        pattern = f"%{search.lower()}%"
        conditions = [
            func.lower(field).like(pattern) for field in self.searchable_fields
        ]
        return stmt.where(or_(*conditions))

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        search: Optional[str] = None,
    ) -> tuple[Sequence[ModelType], int]:
        """
        Retrieve a paginated set of entities.

        Returns both the result set and the total count for pagination metadata.
        """

        stmt = self._apply_search(self._base_select(), search)
        result = await self.session.execute(
            stmt.offset(offset).limit(limit)
        )
        items = result.scalars().all()

        count_stmt = select(func.count()).select_from(self.model)
        count_stmt = self._apply_search(count_stmt, search)  # type: ignore[arg-type]
        total = await self.session.scalar(count_stmt)

        return items, int(total or 0)

    async def get(self, entity_id: Any) -> Optional[ModelType]:
        """Fetch a single entity by primary key."""

        return await self.session.get(self.model, entity_id)

    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new entity using the provided data mapping."""

        entity = self.model(**data)
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(
        self,
        entity: ModelType,
        data: Dict[str, Any],
    ) -> ModelType:
        """Update an existing entity in place."""

        for key, value in data.items():
            setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Delete an entity."""

        await self.session.delete(entity)
