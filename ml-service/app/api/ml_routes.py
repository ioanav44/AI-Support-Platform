from fastapi import APIRouter, HTTPException
from app.api.schemas import ClusterRequest, ClusterResponse, AnomalyRequest, AnomalyResponse
from app.services.clustering import clustering_service
from app.models.anomaly import anomaly_detector
import logging

logger = logging.getLogger(__name__)

clustering_router = APIRouter(prefix="/clustering", tags=["Clustering"])
anomaly_router = APIRouter(prefix="/anomalies", tags=["Anomalies"])

@clustering_router.post("/cluster", response_model=ClusterResponse)
async def cluster_embeddings(request: ClusterRequest):
    """Cluster embeddings using HDBSCAN"""
    try:
        cluster_labels, outlier_scores = clustering_service.cluster(request.embeddings)
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        
        return ClusterResponse(
            cluster_labels=cluster_labels,
            outlier_scores=outlier_scores,
            n_clusters=n_clusters
        )
    except Exception as e:
        logger.error(f"Error clustering embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@anomaly_router.post("/detect", response_model=AnomalyResponse)
async def detect_anomalies(request: AnomalyRequest):
    """Detect anomalies using Z-score method"""
    try:
        zscores = anomaly_detector.compute_zscore(request.values)
        threshold = request.threshold or 2.0
        anomalies = [z > threshold for z in zscores]
        n_anomalies = sum(anomalies)
        
        return AnomalyResponse(
            anomalies=anomalies,
            zscores=zscores,
            n_anomalies=n_anomalies
        )
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@anomaly_router.post("/baseline")
async def update_baseline(metric_name: str, values: list):
    """Update baseline statistics for a metric"""
    try:
        anomaly_detector.update_baseline(metric_name, values)
        return {"status": "baseline updated", "metric": metric_name}
    except Exception as e:
        logger.error(f"Error updating baseline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
