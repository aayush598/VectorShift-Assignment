# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.core.logging import setup_logging
from app.core.rate_limiter import (
    limiter,
    rate_limit_exceeded_handler,
    rate_limit_exception,
)

from app.middleware.logging import RequestLoggingMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.pipelines import router as pipelines_router


# ===============================
# LOGGING
# ===============================
setup_logging()


# ===============================
# FASTAPI APP
# ===============================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise-grade pipeline graph analysis service",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


# ===============================
# RATE LIMITING
# ===============================
app.state.limiter = limiter
app.add_exception_handler(
    rate_limit_exception,
    rate_limit_exceeded_handler,
)


# ===============================
# MIDDLEWARE
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(RequestLoggingMiddleware)


# ===============================
# ROUTERS
# ===============================
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(pipelines_router)
