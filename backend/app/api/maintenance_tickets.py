"""Maintenance ticket API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from ..core.config import settings
from ..schemas import (
    PaginatedResponse,
    PaginationQuery,
    TicketCreate,
    TicketRead,
    TicketUpdate,
)
from ..services import MaintenanceTicketService
from .deps import get_pagination_params, get_ticket_service

from ..models.user import User
from .deps import get_current_user

router = APIRouter(
    prefix="/api/v1/maintenance-tickets",
    tags=["Maintenance Tickets"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "",
    response_model=PaginatedResponse[TicketRead],
    status_code=status.HTTP_200_OK,
)
async def list_tickets(
    pagination: PaginationQuery = Depends(get_pagination_params),
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> PaginatedResponse[TicketRead]:
    """
    List maintenance tickets with optional search and pagination.
    """

    limit = pagination.limit or settings.pagination_default_limit
    offset = pagination.offset or 0
    return await service.list_tickets(
        limit=limit,
        offset=offset,
        search=pagination.search,
    )


@router.get(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
)
async def get_ticket(
    ticket_id: int,
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> TicketRead:
    """
    Retrieve a maintenance ticket by its identifier.
    """

    return await service.get_ticket(ticket_id)


@router.post(
    "",
    response_model=TicketRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_ticket(
    payload: TicketCreate,
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> TicketRead:
    """
    Create a new maintenance ticket.
    """

    return await service.create_ticket(payload)


@router.put(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
)
async def update_ticket(
    ticket_id: int,
    payload: TicketCreate,
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> TicketRead:
    """
    Replace an existing maintenance ticket.
    """

    return await service.update_ticket(
        ticket_id,
        TicketUpdate(**payload.dict()),
    )


@router.patch(
    "/{ticket_id}",
    response_model=TicketRead,
    status_code=status.HTTP_200_OK,
)
async def partial_update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> TicketRead:
    """
    Apply a partial update to an existing maintenance ticket.
    """

    return await service.update_ticket(ticket_id, payload)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_ticket(
    ticket_id: int,
    service: MaintenanceTicketService = Depends(get_ticket_service),
) -> Response:
    """
    Delete a maintenance ticket.
    """

    await service.delete_ticket(ticket_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
