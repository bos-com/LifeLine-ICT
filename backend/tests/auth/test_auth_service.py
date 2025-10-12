
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.services.auth_service import AuthService


@pytest.fixture
def user_repository() -> UserRepository:
    return AsyncMock(spec=UserRepository)


@pytest.mark.asyncio
async def test_create_user(user_repository: UserRepository) -> None:
    auth_service = AuthService(user_repository)
    user = await auth_service.create_user("testuser", "testpassword")

    user_repository.create.assert_called_once()
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_with_valid_credentials(
    user_repository: UserRepository,
) -> None:
    auth_service = AuthService(user_repository)
    user = User(username="testuser", hashed_password=auth_service.get_password_hash("testpassword"))
    user_repository.get_user_by_username.return_value = user

    authenticated_user = await auth_service.authenticate_user("testuser", "testpassword")

    assert authenticated_user == user


@pytest.mark.asyncio
async def test_authenticate_user_with_invalid_credentials(
    user_repository: UserRepository,
) -> None:
    auth_service = AuthService(user_repository)
    user_repository.get_user_by_username.return_value = None

    authenticated_user = await auth_service.authenticate_user("testuser", "testpassword")

    assert authenticated_user is None
