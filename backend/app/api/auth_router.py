
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..repositories.user_repository import UserRepository
from ..services.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES, AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    user_repository = UserRepository(session)
    return AuthService(user_repository)


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users")
async def create_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    user = await auth_service.create_user(form_data.username, form_data.password)
    return {"username": user.username}
