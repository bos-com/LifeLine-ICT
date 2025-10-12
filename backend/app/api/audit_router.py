"""Audit log API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from ..schemas import (
    AuditLogCreate,
    AuditLogQuery,
    AuditLogRead,
    PaginatedResponse,
)
from ..services import AuditLogService
from .deps import get_audit_log_service, get_current_user

router = APIRouter(
    prefix="/api/v1/audit-logs",
    tags=["Audit Logs"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogRead],
    status_code=status.HTTP_200_OK,
)
async def list_audit_logs(
    query: AuditLogQuery = Depends(),
    service: AuditLogService = Depends(get_audit_log_service),
) -> PaginatedResponse[AuditLogRead]:
    """
    Retrieve audit log entries with pagination and filtering.
    """

    return await service.list_logs(query)


@router.get(
    "/{log_id}",
    response_model=AuditLogRead,
    status_code=status.HTTP_200_OK,
)
async def get_audit_log(
    log_id: int,
    service: AuditLogService = Depends(get_audit_log_service),
) -> AuditLogRead:
    """
    Fetch a single audit log entry by its identifier.
    """

    return await service.get_log(log_id)


@router.post(
    "",
    response_model=AuditLogRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit_log(
    payload: AuditLogCreate,
    service: AuditLogService = Depends(get_audit_log_service),
) -> AuditLogRead:
    """
    Record a new audit log entry.
    """

    return await service.record_event(payload)
