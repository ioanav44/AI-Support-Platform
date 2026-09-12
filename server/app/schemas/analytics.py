"""
Pydantic v2 Schemas for Analytics & Ask Support Data.
"""
from pydantic import BaseModel, Field
from typing import Any, Optional


class OverviewMetrics(BaseModel):
    """Dashboard overview metrics."""
    total_tickets: int
    active_issues: int
    critical_issues: int
    avg_sentiment: float
    tickets_today: int
    tickets_this_hour: int
    top_categories: list[dict[str, Any]]
    sentiment_distribution: dict[str, int]


class VolumeSeriesPoint(BaseModel):
    """A single point in the volume time series."""
    timestamp: str
    volume: int
    baseline: float


class VolumeSeriesResponse(BaseModel):
    """Time series of ticket volume vs baseline."""
    series: list[VolumeSeriesPoint]
    interval: str


class AskRequest(BaseModel):
    """Natural language question from the user."""
    question: str = Field(..., min_length=3, max_length=500)


class AskResponse(BaseModel):
    """Response to a natural language question."""
    answer: str
    data: Optional[list[dict[str, Any]]] = None
    sql_query: Optional[str] = None
    confidence: float = 0.0


class SimulationTrigger(BaseModel):
    """Schema for triggering a simulation scenario."""
    scenario: str = Field(..., pattern="^(visa_outage|login_bug|delivery_delay|mobile_crash|subscription_issue)$")
    speed: int = Field(default=5, ge=1, le=20)
    ticket_count: int = Field(default=150, ge=10, le=500)


class SimulationStatus(BaseModel):
    """Status of a running simulation."""
    scenario: str
    status: str  # RUNNING, COMPLETED, STOPPED
    tickets_injected: int
    total_planned: int
    elapsed_seconds: float
