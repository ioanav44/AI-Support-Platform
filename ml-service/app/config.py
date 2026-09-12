from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API
    api_title: str = "AI Support Platform ML Service"
    api_version: str = "1.0.0"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "pulseai_db"
    db_user: str = "pulseai_admin"
    db_password: str = "pulseai_secret_pass"
    
    # ML Models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    
    # HDBSCAN Clustering
    hdbscan_min_cluster_size: int = 5
    hdbscan_min_samples: int = 1
    
    # Anomaly Detection
    zscore_threshold: float = 2.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
