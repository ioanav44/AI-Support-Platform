"""
AI Support Platform Configuration - Environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Support Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://pulseai_admin:pulseai_secret_pass@localhost:5432/pulseai_db"
    DATABASE_URL_SYNC: str = "postgresql+psycopg2://pulseai_admin:pulseai_secret_pass@localhost:5432/pulseai_db"

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o-mini"

    # Embedding
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Clustering Thresholds
    COSINE_SIMILARITY_THRESHOLD: float = 0.82
    MIN_CLUSTER_SIZE: int = 5
    OUTLIER_BUFFER_TRIGGER: int = 15

    # Anomaly Detection Thresholds
    ZSCORE_THRESHOLD: float = 3.5
    VOLUME_SPIKE_MULTIPLIER: float = 3.0
    MIN_SPIKE_TICKETS: int = 8
    SENTIMENT_NEGATIVE_THRESHOLD: float = -0.35
    ANOMALY_WINDOW_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
