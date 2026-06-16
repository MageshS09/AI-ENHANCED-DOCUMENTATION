"""Small in-memory rate limiter for public MVP deployments."""

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests per client IP over a rolling time window.

    This is intentionally lightweight for an MVP. For multi-instance production
    deployments, replace it with Redis-backed limiting.
    """

    def __init__(
        self,
        app: object,
        *,
        requests_per_window: int,
        window_seconds: int,
        protected_paths: tuple[str, ...] = ("/api/generate",),
    ) -> None:
        """Create the rate limiter."""
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.protected_paths = protected_paths
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Reject requests once a client exceeds the configured rate."""
        if not request.url.path.startswith(self.protected_paths):
            return await call_next(request)

        client_id = self._client_id(request)
        now = time.monotonic()
        client_requests = self.requests[client_id]

        while client_requests and now - client_requests[0] > self.window_seconds:
            client_requests.popleft()

        if len(client_requests) >= self.requests_per_window:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
            )

        client_requests.append(now)
        return await call_next(request)

    def _client_id(self, request: Request) -> str:
        """Resolve a stable client identifier from proxy headers or socket info."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
        if request.client:
            return request.client.host
        return "unknown"
