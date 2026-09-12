"""
Anomaly Detection Service — Statistical spike detection using Z-Score against historical baselines.

Evaluates cluster volume against category/day/hour baselines to identify emerging issues.
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.baseline import BaselineMetric
from app.models.issue import EmergingIssue
from app.models.timeline import IssueTimelineEvent

logger = logging.getLogger(__name__)

EPSILON = 0.1  # Prevent division by zero in Z-score


class AnomalyService:
    """Detects anomalous ticket volume spikes against historical baselines."""

    async def get_baseline(
        self, db: AsyncSession, category: str, dt: Optional[datetime] = None
    ) -> tuple[float, float, float]:
        """
        Get the baseline (avg_volume, std_volume, avg_sentiment) for a category
        at a specific day-of-week and hour.
        Returns (avg, std, sentiment) or defaults if no baseline exists.
        """
        if dt is None:
            dt = datetime.now(timezone.utc)

        stmt = select(BaselineMetric).where(
            BaselineMetric.category == category,
            BaselineMetric.day_of_week == dt.weekday(),
            BaselineMetric.hour_of_day == dt.hour,
        )
        result = await db.execute(stmt)
        baseline = result.scalar_one_or_none()

        if baseline:
            return (baseline.avg_hourly_volume, baseline.std_hourly_volume, baseline.avg_sentiment)

        # Default baseline if no historical data
        return (5.0, 2.0, -0.1)

    def compute_anomaly_score(
        self,
        current_volume: int,
        avg_baseline: float,
        std_baseline: float,
        avg_sentiment: float,
        baseline_sentiment: float,
    ) -> dict:
        """
        Compute anomaly metrics for a cluster.
        Returns a dict with z_score, volume_ratio, sentiment_shift, is_anomalous, severity, confidence.
        """
        # Z-Score calculation
        z_score = (current_volume - avg_baseline) / (std_baseline + EPSILON)

        # Volume ratio
        volume_ratio = current_volume / max(avg_baseline, 0.5)

        # Sentiment shift
        sentiment_shift = avg_sentiment - baseline_sentiment

        # Anomaly detection rules
        volume_spike = volume_ratio >= settings.VOLUME_SPIKE_MULTIPLIER or z_score >= settings.ZSCORE_THRESHOLD
        negative_sentiment = avg_sentiment < settings.SENTIMENT_NEGATIVE_THRESHOLD
        sufficient_volume = current_volume >= settings.MIN_SPIKE_TICKETS

        is_anomalous = volume_spike and sufficient_volume

        # Severity calculation
        severity = self._compute_severity(volume_ratio, z_score, negative_sentiment)

        # Confidence score (0.0 to 1.0)
        confidence = min(1.0, (
            0.4 * min(z_score / 5.0, 1.0) +
            0.3 * min(volume_ratio / 6.0, 1.0) +
            0.2 * (1.0 if negative_sentiment else 0.3) +
            0.1 * min(current_volume / 50.0, 1.0)
        ))

        return {
            "z_score": round(z_score, 2),
            "volume_ratio": round(volume_ratio, 2),
            "volume_growth_pct": round((volume_ratio - 1.0) * 100, 1),
            "sentiment_shift": round(sentiment_shift, 3),
            "is_anomalous": is_anomalous,
            "severity": severity,
            "confidence": round(confidence, 2),
        }

    def _compute_severity(self, volume_ratio: float, z_score: float, negative_sentiment: bool) -> str:
        """Compute dynamic severity level based on volume ratio and sentiment."""
        if volume_ratio > 5.0 or z_score > 6.0:
            return "CRITICAL"
        elif volume_ratio > 3.5 or z_score > 4.5:
            return "HIGH"
        elif volume_ratio > 2.0 or z_score > 3.0:
            return "MEDIUM"
        else:
            return "LOW"

    async def check_existing_issue(
        self, db: AsyncSession, cluster_id: uuid.UUID
    ) -> Optional[EmergingIssue]:
        """Check if an active emerging issue already exists for this cluster."""
        stmt = select(EmergingIssue).where(
            EmergingIssue.cluster_id == cluster_id,
            EmergingIssue.status.in_(["DETECTED", "INVESTIGATING"]),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_emerging_issue(
        self,
        db: AsyncSession,
        cluster_id: uuid.UUID,
        category: str,
        anomaly_data: dict,
        ticket_count: int,
        avg_sentiment: float,
        sample_messages: list[str],
        key_terms: list[str],
        affected_demographics: dict,
    ) -> EmergingIssue:
        """Create a new emerging issue from anomaly detection results."""
        now = datetime.now(timezone.utc)

        # Build explainability breakdown
        why_breakdown = {
            "volume_ratio": f"Ticket volume is {anomaly_data['volume_ratio']}x above the historical baseline.",
            "z_score": f"Statistical Z-Score of {anomaly_data['z_score']} exceeds the threshold of {settings.ZSCORE_THRESHOLD}.",
            "sentiment": f"Average sentiment score is {avg_sentiment:.2f} (threshold: {settings.SENTIMENT_NEGATIVE_THRESHOLD}).",
            "ticket_count": f"{ticket_count} related tickets detected in the last {settings.ANOMALY_WINDOW_MINUTES} minutes.",
        }

        # Temporary title & summary (will be enriched by LLM later)
        title = f"{category.replace('_', ' ').title()} Issue Spike"
        summary = (
            f"Detected a {anomaly_data['volume_growth_pct']}% increase in {category} tickets. "
            f"{ticket_count} related tickets found with an average sentiment of {avg_sentiment:.2f}."
        )

        issue = EmergingIssue(
            cluster_id=cluster_id,
            title=title,
            summary=summary,
            severity=anomaly_data["severity"],
            status="DETECTED",
            confidence_score=anomaly_data["confidence"],
            ticket_count=ticket_count,
            baseline_volume=anomaly_data.get("baseline_volume", 5.0),
            volume_growth_pct=anomaly_data["volume_growth_pct"],
            sentiment_avg=avg_sentiment,
            first_detected_at=now,
            last_updated_at=now,
            affected_demographics=affected_demographics,
            key_terms=key_terms,
            why_detected_breakdown=why_breakdown,
        )
        db.add(issue)
        await db.flush()

        # Create initial timeline event
        event = IssueTimelineEvent(
            issue_id=issue.id,
            timestamp=now,
            event_type="DETECTED",
            title="Issue Detected",
            description=f"Anomalous ticket volume detected: {ticket_count} tickets, {anomaly_data['severity']} severity.",
            metadata_={"anomaly_data": anomaly_data},
        )
        db.add(event)
        await db.flush()

        logger.warning(f"Emerging issue created: {title} (severity={anomaly_data['severity']}, confidence={anomaly_data['confidence']})")
        return issue

    async def update_issue_severity(
        self, db: AsyncSession, issue: EmergingIssue, new_severity: str, anomaly_data: dict
    ):
        """Escalate or de-escalate issue severity and log timeline event."""
        old_severity = issue.severity
        if old_severity == new_severity:
            return

        now = datetime.now(timezone.utc)
        issue.severity = new_severity
        issue.last_updated_at = now

        event = IssueTimelineEvent(
            issue_id=issue.id,
            timestamp=now,
            event_type="SEVERITY_ESCALATED",
            title=f"Severity Changed: {old_severity} → {new_severity}",
            description=f"Volume growth now at {anomaly_data['volume_growth_pct']}%. Z-Score: {anomaly_data['z_score']}.",
            metadata_={"old_severity": old_severity, "new_severity": new_severity},
        )
        db.add(event)
        await db.flush()

        logger.warning(f"Issue '{issue.title}' escalated from {old_severity} to {new_severity}")


anomaly_service = AnomalyService()
