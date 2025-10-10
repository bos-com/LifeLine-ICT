"""
Base service helpers encapsulating shared logic.

Services orchestrate repositories and embed business rules that are meaningful
to LifeLine-ICT stakeholders. Keeping them separate allows us to reuse logic in
CLI scripts, background jobs, and API endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas import BaseSchema, PaginatedResponse, PaginationMeta
from .exceptions import NotFoundError


class BaseService:
    """Provide convenience methods shared by concrete services."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

SchemaType = TypeVar("SchemaType", bound=BaseSchema)


    def build_paginated_response(
        self,
        *,
        items: Sequence[Any],
        total: int,
        limit: int,
        offset: int,
        schema: Type[SchemaType],
    ) -> PaginatedResponse[SchemaType]:
        """
        Convert ORM objects into a paginated schema response.

        Parameters
        ----------
        items:
            Iterable of ORM objects.
        total:
            Total number of matching items.
        limit:
            Page size.
        offset:
            Offset used for the query.
        schema:
            Pydantic schema used for serialisation.
        """

        data = [schema.from_orm(item) for item in items]
        return PaginatedResponse[SchemaType](
            data=data,
            pagination=PaginationMeta(total=total, limit=limit, offset=offset),
        )

    @staticmethod
    def ensure_entity(entity: Optional[Any], message: str) -> Any:
        """
        Raise a ``NotFoundError`` if the entity is ``None``.
        """

        if entity is None:
            raise NotFoundError(message)
        return entity
