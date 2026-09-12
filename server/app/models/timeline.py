"""
Issue Timeline Event ORM Model — Tracks the lifecycle of an emerging issue.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class IssueTimelineEvent(Base):
    __tablename__ = "issue_timeline_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("emerging_issues.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    event_type = Column(String(50), nullable=False)  # DETECTED, SEVERITY_ESCALATED, VOLUME_SPIKE, STATUS_CHANGED, RESOLVED
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, nullable=True)

    def __repr__(self):
        return f"<TimelineEvent {self.event_type} at {self.timestamp}>"
