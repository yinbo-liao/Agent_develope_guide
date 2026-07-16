from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory limiter for Wave 1 local development."""

    def __init__(self, app) -> None:
        super().__init__(app)
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._limit = settings.REQUESTS_PER_MINUTE
        self._window_seconds = 60.0

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        history = self._requests[client_ip]

        while history and now - history[0] > self._window_seconds:
            history.popleft()

        if len(history) >= self._limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please retry in a minute."},
            )

        history.append(now)
        return await call_next(request)
