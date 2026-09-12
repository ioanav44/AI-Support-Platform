"""
Embedding Service — Local CPU embedding using FastEmbed (all-MiniLM-L6-v2).

Zero API cost, <10ms per text, fully offline capable.
"""
import logging
from typing import Union
from fastembed import TextEmbedding

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton service that manages a local ONNX embedding model."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _ensure_model(self):
        """Lazily load the embedding model on first use."""
        if self._model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self._model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully.")

    def embed_text(self, text: str) -> list[float]:
        """Generate a 384-dimensional embedding vector for a single text."""
        self._ensure_model()
        embeddings = list(self._model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a batch of texts."""
        self._ensure_model()
        embeddings = list(self._model.embed(texts))
        return [e.tolist() for e in embeddings]


# Module-level singleton
embedding_service = EmbeddingService()
