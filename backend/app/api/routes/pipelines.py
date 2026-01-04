# app/api/routes/pipelines.py

import time
import logging
from fastapi import APIRouter, Request, status, HTTPException
from app.models.pipeline import Pipeline, PipelineResponse
from app.services.pipeline_analyzer import analyze_pipeline
from app.services.cache import SimpleCache
from app.utils.hashing import generate_cache_key
from app.core.config import settings
from app.core.rate_limiter import limiter

router = APIRouter(
    prefix="/pipelines",
    tags=["Pipeline"],
)

logger = logging.getLogger(__name__)
cache = SimpleCache()


@router.post(
    "/parse",
    response_model=PipelineResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit(settings.RATE_LIMIT_PARSE)
async def parse_pipeline(request: Request, pipeline: Pipeline):
    start_time = time.time()
    cache_hit = False

    try:
        if settings.ENABLE_CACHING:
            cache_key = generate_cache_key(pipeline)
            cached = cache.get(cache_key)

            if cached is not None:
                cache_hit = True
                num_nodes, num_edges, is_dag, cycle = cached
                return PipelineResponse(
                    num_nodes=num_nodes,
                    num_edges=num_edges,
                    is_dag=is_dag,
                    cycle=cycle,
                    cache_hit=True,
                    process_time=time.time() - start_time,
                )

        logger.info(
            "Analyzing pipeline | nodes=%s edges=%s",
            len(pipeline.nodes),
            len(pipeline.edges),
        )

        num_nodes, num_edges, is_dag, cycle = analyze_pipeline(pipeline)

        if settings.ENABLE_CACHING:
            cache.set(
                cache_key,
                (num_nodes, num_edges, is_dag, cycle),
            )

        return PipelineResponse(
            num_nodes=num_nodes,
            num_edges=num_edges,
            is_dag=is_dag,
            cycle=cycle,
            cache_hit=cache_hit,
            process_time=time.time() - start_time,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    except Exception as exc:
        logger.exception("Unhandled pipeline error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during pipeline analysis",
        )
