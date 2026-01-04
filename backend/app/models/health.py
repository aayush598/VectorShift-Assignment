# app/models/health.py

from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str


class MetricsResponse(BaseModel):
    cache_stats: Dict[str, Any]
    config: Dict[str, Any]
