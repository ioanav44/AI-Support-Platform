"""
Pipeline Service — Orchestrates the full ticket ingestion pipeline.

Ticket → Preprocess → Sentiment → Embed → Cluster → Anomaly Check → Issue Creation → WebSocket Push
"""
import logging
import re
import uuid
from datetime import datetime, timezone
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.models.ticket import Ticket
from app.models.issue import EmergingIssueTicket
from app.services.embedding_service import embedding_service
from app.services.sentiment_service import compute_sentiment
from app.services.clustering_service import clustering_service
from app.services.anomaly_service import anomaly_service
from app.services.websocket_manager import manager as ws_manager
from app.schemas.ticket import TicketCreate

logger = logging.getLogger(__name__)


def preprocess_text(text: str) -> str:
    """
    Clean and normalize ticket message text.
    - Strip HTML tags
    - Mask credit card numbers
    - Mask email addresses
    - Normalize whitespace
    """
    # Strip HTML
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Mask credit card patterns
    cleaned = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[CARD_MASKED]", cleaned)
    # Mask email addresses
    cleaned = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL_MASKED]", cleaned)
    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_key_terms(messages: list[str], top_n: int = 6) -> list[str]:
    """Extract the most frequent meaningful terms from a list of messages."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "to", "of",
        "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "during", "before", "after", "above", "below", "between", "out", "off",
        "over", "under", "again", "further", "then", "once", "here", "there",
        "when", "where", "why", "how", "all", "each", "every", "both", "few",
        "more", "most", "other", "some", "such", "no", "nor", "not", "only",
        "own", "same", "so", "than", "too", "very", "just", "because", "but",
        "and", "or", "if", "while", "that", "this", "it", "its", "my", "your",
        "i", "me", "we", "you", "he", "she", "they", "them", "his", "her",
        "our", "their", "what", "which", "who", "whom", "get", "got",
    }

    word_counter = Counter()
    for msg in messages:
        words = re.findall(r"\b[a-zA-Z]{3,}\b", msg.lower())
        meaningful = [w for w in words if w not in stop_words]
        word_counter.update(meaningful)

    return [word for word, _ in word_counter.most_common(top_n)]


async def process_ticket(db: AsyncSession, ticket_data: TicketCreate) -> dict:
    """
    Full pipeline for processing a single ticket:
    1. Preprocess text
    2. Compute sentiment
    3. Generate embedding
    4. Save to database
    5. Assign to cluster
    6. Check for anomalies
    7. Push WebSocket notifications
    """
    # 1. Preprocess
    clean_message = preprocess_text(ticket_data.message)

    # 2. Sentiment
    sentiment = compute_sentiment(clean_message)

    # 3. Embedding
    embedding = embedding_service.embed_text(clean_message)

    # 4. Save ticket to DB
    ticket = Ticket(
        ticket_id=ticket_data.ticket_id,
        customer_id=ticket_data.customer_id,
        created_at=ticket_data.created_at,
        message=ticket_data.message,
        category=ticket_data.category,
        priority=ticket_data.priority,
        status=ticket_data.status,
        assigned_agent=ticket_data.assigned_agent,
        channel=ticket_data.channel,
        country=ticket_data.country,
        product=ticket_data.product,
        platform_device=ticket_data.platform_device,
        customer_plan=ticket_data.customer_plan,
        sentiment_score=sentiment,
        embedding=embedding,
    )
    db.add(ticket)
    await db.flush()

    # 5. Cluster assignment
    cluster_match = await clustering_service.find_nearest_cluster(db, embedding)

    if cluster_match:
        cluster_id, similarity = cluster_match
        await clustering_service.assign_to_cluster(db, ticket.id, cluster_id, embedding)
    else:
        # Create new cluster for this ticket
        cluster_id = await clustering_service.create_cluster(
            db, embedding, ticket_data.category, ticket.id
        )
        similarity = 1.0

    # 6. Anomaly detection check
    anomaly_result = await _check_anomaly_for_cluster(db, cluster_id, ticket_data.category)

    # 7. Push real-time update via WebSocket
    await ws_manager.broadcast({
        "event": "TICKET_INGESTED",
        "data": {
            "ticket_id": ticket_data.ticket_id,
            "category": ticket_data.category,
            "sentiment": sentiment,
            "cluster_id": str(cluster_id),
        }
    })

    if anomaly_result and anomaly_result.get("new_issue"):
        await ws_manager.broadcast({
            "event": "EMERGING_ISSUE_DETECTED",
            "data": anomaly_result["issue_data"]
        })

    return {
        "ticket_id": ticket_data.ticket_id,
        "sentiment_score": sentiment,
        "cluster_id": str(cluster_id),
        "similarity": similarity,
        "anomaly_detected": bool(anomaly_result),
    }


async def _check_anomaly_for_cluster(
    db: AsyncSession, cluster_id: uuid.UUID, category: str
) -> dict | None:
    """Run anomaly detection for a cluster after ticket assignment."""
    # Get recent cluster stats
    cluster_stats = await clustering_service.get_recent_cluster_stats(db)

    target_stat = None
    for stat in cluster_stats:
        if stat["cluster_id"] == cluster_id:
            target_stat = stat
            break

    if not target_stat:
        return None

    # Get baseline
    avg_baseline, std_baseline, baseline_sentiment = await anomaly_service.get_baseline(
        db, category
    )

    # Compute anomaly score
    anomaly_data = anomaly_service.compute_anomaly_score(
        current_volume=target_stat["ticket_count"],
        avg_baseline=avg_baseline,
        std_baseline=std_baseline,
        avg_sentiment=target_stat["avg_sentiment"],
        baseline_sentiment=baseline_sentiment,
    )
    anomaly_data["baseline_volume"] = avg_baseline

    if not anomaly_data["is_anomalous"]:
        return None

    # Check if issue already exists
    existing_issue = await anomaly_service.check_existing_issue(db, cluster_id)

    if existing_issue:
        # Update severity if changed
        await anomaly_service.update_issue_severity(db, existing_issue, anomaly_data["severity"], anomaly_data)
        existing_issue.ticket_count = target_stat["ticket_count"]
        existing_issue.volume_growth_pct = anomaly_data["volume_growth_pct"]
        existing_issue.last_updated_at = datetime.now(timezone.utc)
        await db.flush()
        return None  # Not a new issue

    # Get sample messages for key term extraction
    sample_query = text("""
        SELECT message, country, platform_device, customer_plan
        FROM tickets
        WHERE cluster_id = :cid
        ORDER BY created_at DESC LIMIT 20
    """)
    result = await db.execute(sample_query, {"cid": cluster_id})
    samples = result.fetchall()
    sample_messages = [s.message for s in samples]

    # Extract key terms
    key_terms = extract_key_terms(sample_messages)

    # Build demographics
    countries = Counter(s.country for s in samples)
    devices = Counter(s.platform_device for s in samples)
    plans = Counter(s.customer_plan for s in samples)
    demographics = {
        "countries": dict(countries),
        "devices": dict(devices),
        "plans": dict(plans),
    }

    # Create emerging issue
    issue = await anomaly_service.create_emerging_issue(
        db=db,
        cluster_id=cluster_id,
        category=category,
        anomaly_data=anomaly_data,
        ticket_count=target_stat["ticket_count"],
        avg_sentiment=target_stat["avg_sentiment"],
        sample_messages=sample_messages,
        key_terms=key_terms,
        affected_demographics=demographics,
    )

    # Link tickets to issue
    for tid in target_stat["ticket_ids"]:
        link = EmergingIssueTicket(
            issue_id=issue.id,
            ticket_id=tid,
            similarity_score=0.85,  # approximate
        )
        db.add(link)
    await db.flush()

    return {
        "new_issue": True,
        "issue_data": {
            "id": str(issue.id),
            "title": issue.title,
            "severity": issue.severity,
            "confidence_score": issue.confidence_score,
            "ticket_count": issue.ticket_count,
            "volume_growth_pct": issue.volume_growth_pct,
            "first_detected_at": issue.first_detected_at.isoformat(),
            "sentiment_avg": issue.sentiment_avg,
        }
    }
