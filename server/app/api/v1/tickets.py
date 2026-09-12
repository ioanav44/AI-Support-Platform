"""
Tickets API — Ingest and list support tickets.
"""
import asyncio
import logging
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.ticket import Ticket
from app.schemas.ticket import (
    TicketCreate, TicketBatchCreate, TicketResponse, TicketListResponse,
)
from app.services.pipeline_service import process_ticket

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=dict, status_code=201)
async def ingest_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a single ticket through the full processing pipeline."""
    result = await process_ticket(db, ticket_data)
    return result


@router.post("/batch", response_model=dict, status_code=201)
async def ingest_ticket_batch(
    batch: TicketBatchCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a batch of tickets. Processing happens in background."""
    count = len(batch.tickets)

    for ticket_data in batch.tickets:
        try:
            await process_ticket(db, ticket_data)
        except Exception as e:
            logger.error(f"Failed to process ticket {ticket_data.ticket_id}: {e}")

    return {"accepted": count, "status": "processed"}


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    category: str = Query(None),
    status: str = Query(None),
    priority: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List tickets with pagination and filtering."""
    query = select(Ticket)
    count_query = select(func.count(Ticket.id))

    if category:
        query = query.where(Ticket.category == category)
        count_query = count_query.where(Ticket.category == category)
    if status:
        query = query.where(Ticket.status == status)
        count_query = count_query.where(Ticket.status == status)
    if priority:
        query = query.where(Ticket.priority == priority)
        count_query = count_query.where(Ticket.priority == priority)

    # Count total
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Fetch page
    offset = (page - 1) * limit
    query = query.order_by(Ticket.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    tickets = result.scalars().all()

    return TicketListResponse(
        tickets=[TicketResponse.model_validate(t) for t in tickets],
        total=total,
        page=page,
        limit=limit,
    )
