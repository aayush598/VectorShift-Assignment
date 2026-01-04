# app/api/routes/health.py

from fastapi import APIRouter, Request
from datetime import datetime
from app.models.health import HealthResponse
from app.core.config import settings
from app.core.rate_limiter import limiter

router = APIRouter(tags=["Health"])


@router.get("/")
@limiter.limit(settings.RATE_LIMIT_ANONYMOUS)
async def root(request: Request):
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health",
    }


@router.get("/health", response_model=HealthResponse)
@limiter.limit(settings.RATE_LIMIT_ANONYMOUS)
async def health_check(request: Request):
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
    )
