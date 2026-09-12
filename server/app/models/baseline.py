"""
Baseline Metric ORM Model — Historical averages per category/hour/day for anomaly detection.
"""
from sqlalchemy import Column, String, Integer, Float, UniqueConstraint

from app.core.database import Base


class BaselineMetric(Base):
    __tablename__ = "baseline_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(50), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer, nullable=False)   # 0-23
    avg_hourly_volume = Column(Float, nullable=False)
    std_hourly_volume = Column(Float, nullable=False)
    avg_sentiment = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("category", "day_of_week", "hour_of_day", name="uq_baseline_cat_day_hour"),
    )

    def __repr__(self):
        return f"<Baseline {self.category} dow={self.day_of_week} h={self.hour_of_day} avg={self.avg_hourly_volume:.1f}>"
