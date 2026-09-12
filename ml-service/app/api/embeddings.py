from fastapi import APIRouter, HTTPException
from app.api.schemas import EmbedRequest, EmbedResponse, EmbedBatchRequest
from app.models.embedding import embedding_model
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/embeddings", tags=["Embeddings"])

@router.post("/generate", response_model=EmbedResponse)
async def generate_embedding(request: EmbedRequest):
    """Generate embedding for a single text"""
    try:
        embedding = embedding_model.embed(request.text)
        return EmbedResponse(
            embedding=embedding,
            dimension=len(embedding)
        )
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-batch")
async def generate_embeddings_batch(request: EmbedBatchRequest):
    """Generate embeddings for multiple texts"""
    try:
        embeddings = embedding_model.embed_batch(request.texts)
        return {
            "embeddings": embeddings,
            "dimension": len(embeddings[0]) if embeddings else 0,
            "count": len(embeddings)
        }
    except Exception as e:
        logger.error(f"Error generating batch embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    """Health check for embedding service"""
    return {
        "status": "ok",
        "service": "embedding-model",
        "dimension": embedding_model.get_dimension()
    }
