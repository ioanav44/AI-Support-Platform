import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self, zscore_threshold: float = 2.0):
        self.zscore_threshold = zscore_threshold
        self.baseline_stats = {}
    
    def compute_zscore(self, values: list, metric_name: str = "default") -> list:
        """
        Compute Z-score for anomaly detection.
        Returns list of (value, zscore) tuples.
        """
        arr = np.array(values, dtype=float)
        mean = np.mean(arr)
        std = np.std(arr)
        
        if std == 0:
            zscores = np.zeros_like(arr)
        else:
            zscores = np.abs((arr - mean) / std)
        
        return list(zscores)
    
    def detect_anomalies(self, values: list, threshold: float = None) -> list:
        """
        Detect anomalies using Z-score method.
        Returns list of booleans indicating anomalies.
        """
        threshold = threshold or self.zscore_threshold
        zscores = self.compute_zscore(values)
        anomalies = [z > threshold for z in zscores]
        
        logger.info(f"Detected {sum(anomalies)} anomalies out of {len(anomalies)} values")
        return anomalies
    
    def update_baseline(self, metric_name: str, values: list):
        """Update baseline statistics for a metric"""
        arr = np.array(values, dtype=float)
        self.baseline_stats[metric_name] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr))
        }
        logger.info(f"Updated baseline for {metric_name}")

anomaly_detector = AnomalyDetector()
