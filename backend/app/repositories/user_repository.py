
from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User
from .base import AsyncRepository


class UserRepository(AsyncRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(self._model).where(self._model.username == username)
        )
        return result.scalars().first()
