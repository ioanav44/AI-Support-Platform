"""
Ticket ORM Model — A customer support ticket with embedding vector.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="open")
    assigned_agent = Column(String(100), nullable=True)
    channel = Column(String(30), nullable=False)
    country = Column(String(10), nullable=False)
    product = Column(String(50), nullable=False)
    platform_device = Column(String(50), nullable=False)
    customer_plan = Column(String(30), nullable=False)
    sentiment_score = Column(Float, nullable=False)
    embedding = Column(Vector(384), nullable=False)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("clusters.id", ondelete="SET NULL"), nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_tickets_created_at", "created_at"),
        Index("idx_tickets_category", "category"),
        Index("idx_tickets_status", "status"),
    )

    def __repr__(self):
        return f"<Ticket {self.ticket_id} category={self.category} priority={self.priority}>"
