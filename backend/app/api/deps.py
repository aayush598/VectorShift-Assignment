# app/api/deps.py

from fastapi import Request
from app.core.rate_limiter import limiter


def get_limiter(request: Request):
    return limiter
