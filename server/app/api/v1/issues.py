"""
Issues API — Emerging issues CRUD and lifecycle management.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from uuid import UUID

from app.core.database import get_db
from app.models.issue import EmergingIssue, EmergingIssueTicket
from app.models.timeline import IssueTimelineEvent
from app.models.ticket import Ticket
from app.schemas.issue import (
    EmergingIssueResponse, EmergingIssueListResponse,
    IssueStatusUpdate, IssueDetailResponse, TimelineEventResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/issues", tags=["Emerging Issues"])


@router.get("", response_model=EmergingIssueListResponse)
async def list_issues(
    status: str = Query(None),
    severity: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all emerging issues with optional filtering."""
    query = select(EmergingIssue)

    if status:
        query = query.where(EmergingIssue.status == status)
    if severity:
        query = query.where(EmergingIssue.severity == severity)

    query = query.order_by(EmergingIssue.first_detected_at.desc())
    result = await db.execute(query)
    issues = result.scalars().all()

    return EmergingIssueListResponse(
        issues=[EmergingIssueResponse.model_validate(i) for i in issues],
        total=len(issues),
    )


@router.get("/{issue_id}", response_model=IssueDetailResponse)
async def get_issue_detail(
    issue_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full detail of an emerging issue including timeline and sample tickets."""
    # Get the issue
    issue = await db.get(EmergingIssue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    # Get timeline events
    timeline_query = (
        select(IssueTimelineEvent)
        .where(IssueTimelineEvent.issue_id == issue_id)
        .order_by(IssueTimelineEvent.timestamp.asc())
    )
    timeline_result = await db.execute(timeline_query)
    timeline = timeline_result.scalars().all()

    # Get sample tickets via the association table
    sample_query = text("""
        SELECT t.ticket_id, t.message, t.category, t.priority, t.channel,
               t.country, t.platform_device, t.customer_plan,
               t.sentiment_score, t.created_at, eit.similarity_score
        FROM emerging_issue_tickets eit
        JOIN tickets t ON eit.ticket_id = t.id
        WHERE eit.issue_id = :issue_id
        ORDER BY eit.similarity_score DESC
        LIMIT 20
    """)
    sample_result = await db.execute(sample_query, {"issue_id": issue_id})
    sample_tickets = [
        {
            "ticket_id": row.ticket_id,
            "message": row.message,
            "category": row.category,
            "priority": row.priority,
            "channel": row.channel,
            "country": row.country,
            "platform_device": row.platform_device,
            "customer_plan": row.customer_plan,
            "sentiment_score": row.sentiment_score,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "similarity_score": row.similarity_score,
        }
        for row in sample_result.fetchall()
    ]

    return IssueDetailResponse(
        issue=EmergingIssueResponse.model_validate(issue),
        timeline=[TimelineEventResponse.model_validate(e) for e in timeline],
        sample_tickets=sample_tickets,
    )


@router.patch("/{issue_id}", response_model=EmergingIssueResponse)
async def update_issue_status(
    issue_id: UUID,
    update: IssueStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update the status of an emerging issue."""
    issue = await db.get(EmergingIssue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")

    old_status = issue.status
    now = datetime.now(timezone.utc)

    issue.status = update.status
    issue.last_updated_at = now
    if update.status == "RESOLVED":
        issue.resolved_at = now

    # Log timeline event
    event = IssueTimelineEvent(
        issue_id=issue_id,
        timestamp=now,
        event_type="STATUS_CHANGED",
        title=f"Status Changed: {old_status} → {update.status}",
        description=f"Issue status updated from {old_status} to {update.status}.",
        metadata_={"old_status": old_status, "new_status": update.status},
    )
    db.add(event)
    await db.flush()

    return EmergingIssueResponse.model_validate(issue)
