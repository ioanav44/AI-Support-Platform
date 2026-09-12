"""
Pydantic v2 Schemas for Emerging Issues.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID


class EmergingIssueResponse(BaseModel):
    """Schema for emerging issue API response."""
    id: UUID
    cluster_id: Optional[UUID]
    title: str
    summary: str
    severity: str
    status: str
    confidence_score: float
    ticket_count: int
    baseline_volume: float
    volume_growth_pct: float
    sentiment_avg: float
    first_detected_at: datetime
    last_updated_at: datetime
    resolved_at: Optional[datetime]
    affected_demographics: dict[str, Any]
    key_terms: list[str]
    root_cause_hypothesis: Optional[str]
    why_detected_breakdown: dict[str, Any]

    model_config = {"from_attributes": True}


class EmergingIssueListResponse(BaseModel):
    """List of emerging issues."""
    issues: list[EmergingIssueResponse]
    total: int


class IssueStatusUpdate(BaseModel):
    """Schema for updating issue status."""
    status: str = Field(..., pattern="^(DETECTED|INVESTIGATING|MITIGATED|RESOLVED)$")


class TimelineEventResponse(BaseModel):
    """Schema for timeline event."""
    id: UUID
    issue_id: UUID
    timestamp: datetime
    event_type: str
    title: str
    description: str
    metadata_: Optional[dict[str, Any]] = Field(None, alias="metadata_")

    model_config = {"from_attributes": True}


class IssueDetailResponse(BaseModel):
    """Full detail view of an emerging issue with timeline and related tickets."""
    issue: EmergingIssueResponse
    timeline: list[TimelineEventResponse]
    sample_tickets: list[dict[str, Any]]
