# app/api/routes/metrics.py

from fastapi import APIRouter, Request
from app.models.health import MetricsResponse
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.services.cache import SimpleCache

router = APIRouter(prefix="/metrics", tags=["Monitoring"])

# Shared cache instance (same as pipelines)
cache = SimpleCache()


@router.get("", response_model=MetricsResponse)
@limiter.limit("20/minute")
async def get_metrics(request: Request):
    return MetricsResponse(
        cache_stats=cache.stats(),
        config={
            "max_nodes": settings.MAX_NODES,
            "max_edges": settings.MAX_EDGES,
            "cache_enabled": settings.ENABLE_CACHING,
            "cache_ttl": settings.CACHE_TTL,
        },
    )
