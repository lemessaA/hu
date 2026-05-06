"""Structured logging middleware for FastAPI."""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("agri.http")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "request_failed",
                extra={"request_id": request_id, "path": request.url.path, "ms": duration_ms},
            )
            raise
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request id=%s method=%s path=%s status=%s ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            round(duration_ms, 2),
        )
        response.headers["X-Request-Id"] = request_id
        return response
