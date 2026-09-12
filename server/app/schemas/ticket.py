"""
Pydantic v2 Schemas for Tickets.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class TicketCreate(BaseModel):
    """Schema for creating a new ticket (ingest endpoint)."""
    ticket_id: str = Field(..., max_length=50)
    customer_id: str = Field(..., max_length=50)
    created_at: datetime
    message: str = Field(..., min_length=5)
    category: str = Field(..., max_length=50)
    priority: str = Field(..., pattern="^(low|medium|high|urgent)$")
    status: str = Field(default="open", max_length=20)
    assigned_agent: Optional[str] = None
    channel: str = Field(..., pattern="^(email|chat|web_form|mobile_app|phone)$")
    country: str = Field(..., max_length=10)
    product: str = Field(..., max_length=50)
    platform_device: str = Field(..., max_length=50)
    customer_plan: str = Field(..., pattern="^(Free|Pro|Enterprise)$")


class TicketBatchCreate(BaseModel):
    """Schema for batch ticket ingestion."""
    tickets: list[TicketCreate]


class TicketResponse(BaseModel):
    """Schema for ticket API response."""
    id: UUID
    ticket_id: str
    customer_id: str
    created_at: datetime
    message: str
    category: str
    priority: str
    status: str
    assigned_agent: Optional[str]
    channel: str
    country: str
    product: str
    platform_device: str
    customer_plan: str
    sentiment_score: float
    cluster_id: Optional[UUID]

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    """Paginated ticket list."""
    tickets: list[TicketResponse]
    total: int
    page: int
    limit: int
