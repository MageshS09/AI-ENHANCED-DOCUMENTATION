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

    ``trusted_proxies`` is the number of reverse proxies in front of the app that
    append to ``X-Forwarded-For`` (1 on Render). Each proxy appends the address it
    saw, so the trustworthy client address is the one that many entries from the
    *right*; anything to its left was supplied by the client and can be forged.
    Use 0 to ignore the header entirely when the app is directly exposed.
    """

    def __init__(
        self,
        app: object,
        *,
        requests_per_window: int,
        window_seconds: int,
        protected_paths: tuple[str, ...] = ("/api/generate",),
        trusted_proxies: int = 1,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Create the rate limiter."""
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.protected_paths = protected_paths
        self.trusted_proxies = trusted_proxies
        self.clock = clock
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self._last_sweep = clock()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Reject requests once a client exceeds the configured rate."""
        if request.method == "OPTIONS" or not request.url.path.startswith(self.protected_paths):
            return await call_next(request)

        client_id = self._client_id(request)
        now = self.clock()
        self._sweep(now)
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

    def _sweep(self, now: float) -> None:
        """Drop clients with no recent requests so the table cannot grow without bound."""
        if now - self._last_sweep < self.window_seconds:
            return
        self._last_sweep = now
        stale = [
            client
            for client, stamps in self.requests.items()
            if not stamps or now - stamps[-1] > self.window_seconds
        ]
        for client in stale:
            del self.requests[client]

    def _client_id(self, request: Request) -> str:
        """Resolve the client address using only proxy-supplied header entries."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for and self.trusted_proxies > 0:
            addresses = [part.strip() for part in forwarded_for.split(",") if part.strip()]
            if len(addresses) >= self.trusted_proxies:
                return addresses[-self.trusted_proxies]
        if request.client:
            return request.client.host
        return "unknown"
