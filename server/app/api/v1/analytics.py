"""
Analytics API — Dashboard overview metrics and time series data.
"""
import logging
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text

from app.core.database import get_db
from app.models.ticket import Ticket
from app.models.issue import EmergingIssue
from app.schemas.analytics import OverviewMetrics, VolumeSeriesResponse, VolumeSeriesPoint

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewMetrics)
async def get_overview(db: AsyncSession = Depends(get_db)):
    """Get dashboard overview metrics."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    hour_start = now - timedelta(hours=1)

    # Total tickets
    total_result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = total_result.scalar() or 0

    # Tickets today
    today_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.created_at >= today_start)
    )
    tickets_today = today_result.scalar() or 0

    # Tickets this hour
    hour_result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.created_at >= hour_start)
    )
    tickets_this_hour = hour_result.scalar() or 0

    # Active issues
    active_result = await db.execute(
        select(func.count(EmergingIssue.id)).where(
            EmergingIssue.status.in_(["DETECTED", "INVESTIGATING"])
        )
    )
    active_issues = active_result.scalar() or 0

    # Critical issues
    critical_result = await db.execute(
        select(func.count(EmergingIssue.id)).where(
            EmergingIssue.severity == "CRITICAL",
            EmergingIssue.status.in_(["DETECTED", "INVESTIGATING"]),
        )
    )
    critical_issues = critical_result.scalar() or 0

    # Average sentiment
    sentiment_result = await db.execute(
        select(func.avg(Ticket.sentiment_score))
    )
    avg_sentiment = round(sentiment_result.scalar() or 0, 3)

    # Top categories
    cat_result = await db.execute(
        text("""
            SELECT category, COUNT(*) as count
            FROM tickets
            GROUP BY category
            ORDER BY count DESC
            LIMIT 10
        """)
    )
    top_categories = [
        {"category": row.category, "count": row.count}
        for row in cat_result.fetchall()
    ]

    # Sentiment distribution
    sent_result = await db.execute(
        text("""
            SELECT
                CASE
                    WHEN sentiment_score >= 0.3 THEN 'positive'
                    WHEN sentiment_score <= -0.3 THEN 'negative'
                    ELSE 'neutral'
                END as sentiment_label,
                COUNT(*) as count
            FROM tickets
            GROUP BY sentiment_label
        """)
    )
    sentiment_distribution = {
        row.sentiment_label: row.count for row in sent_result.fetchall()
    }

    return OverviewMetrics(
        total_tickets=total_tickets,
        active_issues=active_issues,
        critical_issues=critical_issues,
        avg_sentiment=avg_sentiment,
        tickets_today=tickets_today,
        tickets_this_hour=tickets_this_hour,
        top_categories=top_categories,
        sentiment_distribution=sentiment_distribution,
    )


@router.get("/volume-series", response_model=VolumeSeriesResponse)
async def get_volume_series(
    hours: int = Query(24, ge=1, le=168),
    interval: str = Query("1h", pattern="^(15m|30m|1h|4h)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get ticket volume time series for the chart."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)

    # Map interval to PostgreSQL date_trunc format
    interval_map = {
        "15m": "15 minutes",
        "30m": "30 minutes",
        "1h": "1 hour",
        "4h": "4 hours",
    }
    pg_interval = interval_map[interval]

    # Volume series query
    query = text(f"""
        WITH time_buckets AS (
            SELECT date_trunc('hour', generate_series(
                :start_time,
                :end_time,
                interval '{pg_interval}'
            )) as bucket
        ),
        ticket_counts AS (
            SELECT
                date_trunc('hour', created_at) as bucket,
                COUNT(*) as volume
            FROM tickets
            WHERE created_at >= :start_time AND created_at <= :end_time
            GROUP BY bucket
        ),
        baseline AS (
            SELECT
                day_of_week,
                hour_of_day,
                avg_hourly_volume
            FROM baseline_metrics
        )
        SELECT
            tb.bucket as timestamp,
            COALESCE(tc.volume, 0) as volume,
            COALESCE(bl.avg_hourly_volume, 5.0) as baseline
        FROM time_buckets tb
        LEFT JOIN ticket_counts tc ON tb.bucket = tc.bucket
        LEFT JOIN baseline bl ON
            EXTRACT(DOW FROM tb.bucket)::int = bl.day_of_week
            AND EXTRACT(HOUR FROM tb.bucket)::int = bl.hour_of_day
        ORDER BY tb.bucket ASC
    """)

    result = await db.execute(query, {"start_time": start, "end_time": now})
    rows = result.fetchall()

    series = [
        VolumeSeriesPoint(
            timestamp=row.timestamp.isoformat() if row.timestamp else "",
            volume=row.volume,
            baseline=round(row.baseline, 1),
        )
        for row in rows
    ]

    return VolumeSeriesResponse(series=series, interval=interval)
