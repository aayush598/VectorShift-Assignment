# app/core/lifespan.py

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from app.core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s", settings.APP_NAME)
    logger.info(
        "Config | MAX_NODES=%s | MAX_EDGES=%s | CACHE=%s",
        settings.MAX_NODES,
        settings.MAX_EDGES,
        settings.ENABLE_CACHING,
    )

    yield

    logger.info("Shutting down %s", settings.APP_NAME)
