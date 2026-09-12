"""
AI Support Platform — Main FastAPI Application Entry Point.

AI-Powered Customer Support Intelligence & Incident Detection Platform.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import tickets, issues, analytics, simulation, ask
from app.api import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("AI Support Platform starting up...")
    logger.info(f"   Environment: {settings.ENVIRONMENT}")
    logger.info(f"   Database: {settings.DATABASE_URL[:50]}...")

    # Initialize database tables
    await init_db()
    logger.info("[OK] Database initialized")

    # Pre-warm the embedding model
    try:
        from app.services.embedding_service import embedding_service
        embedding_service.embed_text("warmup")
        logger.info("[OK] Embedding model loaded and warmed up")
    except Exception as e:
        logger.warning(f"[WARN] Embedding warmup deferred: {e}")

    yield

    logger.info("AI Support Platform shutting down...")


app = FastAPI(
    title="AI Support Platform",
    description=(
        "AI-Powered Customer Support Intelligence Platform. "
        "Real-time semantic clustering, anomaly detection, and incident management "
        "for B2B SaaS support operations."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(tickets.router, prefix="/api/v1")
app.include_router(issues.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(simulation.router, prefix="/api/v1")
app.include_router(ask.router, prefix="/api/v1")
app.include_router(websockets.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "name": "AI Support Platform",
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
