from pydantic import BaseModel
from typing import List

class EmbedRequest(BaseModel):
    text: str

class EmbedBatchRequest(BaseModel):
    texts: List[str]

class EmbedResponse(BaseModel):
    embedding: List[float]
    dimension: int

class ClusterRequest(BaseModel):
    embeddings: List[List[float]]

class ClusterResponse(BaseModel):
    cluster_labels: List[int]
    outlier_scores: List[float]
    n_clusters: int

class AnomalyRequest(BaseModel):
    values: List[float]
    threshold: float = None

class AnomalyResponse(BaseModel):
    anomalies: List[bool]
    zscores: List[float]
    n_anomalies: int

class HealthResponse(BaseModel):
    status: str
    version: str
