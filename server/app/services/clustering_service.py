"""
Clustering Service — Hybrid incremental + batch HDBSCAN clustering.

Online: Assigns new tickets to existing clusters via cosine similarity.
Batch: Periodically runs HDBSCAN on unassigned tickets to discover new clusters.
"""
import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

import numpy as np
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cluster import Cluster
from app.models.ticket import Ticket

logger = logging.getLogger(__name__)


class ClusteringService:
    """Manages incremental ticket-to-cluster assignment and batch re-clustering."""

    async def find_nearest_cluster(
        self, db: AsyncSession, embedding: list[float], time_window_hours: int = 24
    ) -> Optional[tuple[uuid.UUID, float]]:
        """
        Find the nearest cluster centroid within the time window using pgvector cosine distance.
        Returns (cluster_id, similarity_score) or None if no match above threshold.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        vector_str = "[" + ",".join(str(x) for x in embedding) + "]"

        # pgvector cosine distance: 1 - cosine_similarity
        # So we need distance < (1 - threshold)
        max_distance = 1.0 - settings.COSINE_SIMILARITY_THRESHOLD

        query = text("""
            SELECT id, 1 - (centroid_vector <=> :vec::vector) as similarity
            FROM clusters
            WHERE last_updated_at >= :cutoff
            ORDER BY centroid_vector <=> :vec::vector ASC
            LIMIT 1
        """)

        result = await db.execute(
            query,
            {"vec": vector_str, "cutoff": cutoff}
        )
        row = result.fetchone()

        if row and row.similarity >= settings.COSINE_SIMILARITY_THRESHOLD:
            return (row.id, float(row.similarity))

        return None

    async def assign_to_cluster(
        self, db: AsyncSession, ticket_id: uuid.UUID, cluster_id: uuid.UUID,
        embedding: list[float]
    ):
        """
        Assign a ticket to an existing cluster and update the centroid incrementally.
        New centroid = (N * old_centroid + new_vector) / (N + 1)
        """
        cluster = await db.get(Cluster, cluster_id)
        if not cluster:
            return

        old_centroid = np.array(cluster.centroid_vector)
        new_vec = np.array(embedding)
        n = cluster.ticket_count

        # Incremental centroid update
        new_centroid = (n * old_centroid + new_vec) / (n + 1)
        new_centroid = new_centroid / np.linalg.norm(new_centroid)  # Re-normalize

        cluster.centroid_vector = new_centroid.tolist()
        cluster.ticket_count = n + 1
        cluster.last_updated_at = datetime.now(timezone.utc)

        # Update ticket's cluster_id
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await db.execute(stmt)
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.cluster_id = cluster_id

        await db.flush()
        logger.info(f"Ticket {ticket_id} assigned to cluster {cluster_id} (size: {n + 1})")

    async def create_cluster(
        self, db: AsyncSession, embedding: list[float], category: str, ticket_id: uuid.UUID
    ) -> uuid.UUID:
        """Create a new cluster from a single ticket."""
        normalized = np.array(embedding)
        normalized = normalized / np.linalg.norm(normalized)

        cluster = Cluster(
            centroid_vector=normalized.tolist(),
            primary_category=category,
            ticket_count=1,
        )
        db.add(cluster)
        await db.flush()

        # Assign ticket to this cluster
        stmt = select(Ticket).where(Ticket.id == ticket_id)
        result = await db.execute(stmt)
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.cluster_id = cluster.id

        await db.flush()
        logger.info(f"New cluster {cluster.id} created for category '{category}'")
        return cluster.id

    async def get_recent_cluster_stats(
        self, db: AsyncSession, window_minutes: int = 30
    ) -> list[dict]:
        """
        Get ticket counts per cluster in the recent time window.
        Used by anomaly detection to identify volume spikes.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

        query = text("""
            SELECT
                t.cluster_id,
                c.primary_category,
                COUNT(*) as ticket_count,
                AVG(t.sentiment_score) as avg_sentiment,
                array_agg(t.id) as ticket_ids
            FROM tickets t
            JOIN clusters c ON t.cluster_id = c.id
            WHERE t.created_at >= :cutoff AND t.cluster_id IS NOT NULL
            GROUP BY t.cluster_id, c.primary_category
            HAVING COUNT(*) >= :min_tickets
            ORDER BY COUNT(*) DESC
        """)

        result = await db.execute(
            query,
            {"cutoff": cutoff, "min_tickets": settings.MIN_SPIKE_TICKETS}
        )

        return [
            {
                "cluster_id": row.cluster_id,
                "category": row.primary_category,
                "ticket_count": row.ticket_count,
                "avg_sentiment": float(row.avg_sentiment),
                "ticket_ids": row.ticket_ids,
            }
            for row in result.fetchall()
        ]


clustering_service = ClusteringService()
