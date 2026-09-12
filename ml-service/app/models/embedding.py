from sentence_transformers import SentenceTransformer
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

class EmbeddingModel:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            settings = get_settings()
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            cls._instance.model = SentenceTransformer(settings.embedding_model)
        return cls._instance
    
    def embed(self, text: str) -> list:
        """Generate embedding for a single text"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_batch(self, texts: list) -> list:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        return len(self.embed("test"))

# Singleton instance
embedding_model = EmbeddingModel()
