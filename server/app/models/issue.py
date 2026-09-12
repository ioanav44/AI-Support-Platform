"""
Emerging Issue & Association ORM Models.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class EmergingIssue(Base):
    __tablename__ = "emerging_issues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(150), nullable=False)
    summary = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(30), nullable=False, default="DETECTED")  # DETECTED, INVESTIGATING, MITIGATED, RESOLVED
    confidence_score = Column(Float, nullable=False)
    ticket_count = Column(Integer, nullable=False)
    baseline_volume = Column(Float, nullable=False)
    volume_growth_pct = Column(Float, nullable=False)
    sentiment_avg = Column(Float, nullable=False)
    first_detected_at = Column(DateTime(timezone=True), nullable=False)
    last_updated_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    affected_demographics = Column(JSONB, nullable=False, default=dict)
    key_terms = Column(JSONB, nullable=False, default=list)
    root_cause_hypothesis = Column(Text, nullable=True)
    why_detected_breakdown = Column(JSONB, nullable=False, default=dict)

    def __repr__(self):
        return f"<EmergingIssue '{self.title}' severity={self.severity} status={self.status}>"


class EmergingIssueTicket(Base):
    __tablename__ = "emerging_issue_tickets"

    issue_id = Column(UUID(as_uuid=True), ForeignKey("emerging_issues.id", ondelete="CASCADE"), primary_key=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True)
    similarity_score = Column(Float, nullable=False)
