
from __future__ import annotations

from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from ..models.user import User
from ..repositories.user_repository import UserRepository

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return crypt_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return crypt_context.hash(password)

    async def create_user(self, username: str, password: str) -> User:
        hashed_password = self.get_password_hash(password)
        user = User(username=username, hashed_password=hashed_password)
        return await self._user_repository.create(user)

    async def authenticate_user(self, username: str, password: str) -> User | None:
        user = await self._user_repository.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
