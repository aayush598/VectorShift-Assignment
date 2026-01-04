# app/middleware/logging.py

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests and outgoing responses with timing.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        client_host = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        logger.info(
            "📥 %s %s | client=%s",
            method,
            path,
            client_host,
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            response.headers["X-Process-Time"] = f"{process_time:.6f}"

            logger.info(
                "📤 %s %s | status=%s | %.3fs",
                method,
                path,
                response.status_code,
                process_time,
            )

            return response

        except Exception:
            process_time = time.time() - start_time

            logger.exception(
                "❌ %s %s | failed after %.3fs",
                method,
                path,
                process_time,
            )
            raise
