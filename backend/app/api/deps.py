from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session, session_scope
from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..services.auth_service import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


from ..services.sensor_sites import SensorSiteService

def get_sensor_site_service(
    session: AsyncSession = Depends(get_session),
) -> SensorSiteService:
    return SensorSiteService(session)


from ..services.resources import ResourceService

def get_resource_service(
    session: AsyncSession = Depends(get_session),
) -> ResourceService:
    return ResourceService(session)


from ..services.projects import ProjectService

def get_project_service(
    session: AsyncSession = Depends(get_session),
) -> ProjectService:
    return ProjectService(session)


from ..services.maintenance_tickets import MaintenanceTicketService

def get_ticket_service(
    session: AsyncSession = Depends(get_session),
) -> MaintenanceTicketService:
    return MaintenanceTicketService(session)


from ..schemas.base import PaginationQuery
from ..core.config import settings

def get_pagination_params(
    limit: int = settings.pagination_default_limit,
    offset: int = 0,
    search: str = None,
) -> PaginationQuery:
    return PaginationQuery(limit=limit, offset=offset, search=search)


from ..services.locations import LocationService
from ..services.audit_log_service import AuditLogService


def get_location_service(
    session: AsyncSession = Depends(get_session),
) -> LocationService:
    return LocationService(session)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Backwards-compatible dependency that yields a database session.
    
    Tests and older routers still import ``get_db_session``; to avoid breaking
    them we forward to the shared session scope used by ``get_session``.
    """
    async with session_scope() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def get_audit_log_service(
    session: AsyncSession = Depends(get_session),
) -> AuditLogService:
    """Provide an audit log service instance for request handlers."""

    return AuditLogService(session)
