import numpy as np
import hdbscan
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class ClusteringService:
    def __init__(self, min_cluster_size: int = 5, min_samples: int = 1):
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.clusterer = None
    
    def cluster(self, embeddings: List[List[float]]) -> Tuple[List[int], List[int]]:
        """
        Cluster embeddings using HDBSCAN.
        
        Returns:
            cluster_labels: List of cluster IDs (-1 for outliers)
            outlier_scores: Soft clustering scores (higher = more anomalous)
        """
        if len(embeddings) < self.min_cluster_size:
            logger.warning(f"Not enough samples for clustering: {len(embeddings)}")
            return list(range(len(embeddings))), [0.0] * len(embeddings)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric='euclidean',
            prediction_data=True
        )
        
        cluster_labels = self.clusterer.fit_predict(embeddings_array)
        
        # Compute outlier scores (higher = more anomalous)
        outlier_scores = self.clusterer.outlier_scores_
        if outlier_scores is None:
            outlier_scores = [0.0] * len(embeddings)
        
        logger.info(f"Clustered {len(embeddings)} samples into {len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)} clusters")
        
        return cluster_labels.tolist(), outlier_scores.tolist()
    
    def predict_incremental(self, new_embeddings: List[List[float]]) -> List[int]:
        """
        Predict cluster labels for new embeddings (requires prior clustering).
        """
        if self.clusterer is None:
            raise ValueError("Must run cluster() first before prediction")
        
        new_embeddings_array = np.array(new_embeddings, dtype=np.float32)
        labels, strengths = hdbscan.approximate_predict(self.clusterer, new_embeddings_array)
        
        return labels.tolist()

clustering_service = ClusteringService()
