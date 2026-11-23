"""Tests for the in-memory rate limiter."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from utils.rate_limit import InMemoryRateLimitMiddleware


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def build(limit: int = 2, window: int = 60, trusted_proxies: int = 1, clock: Clock | None = None):
    app = FastAPI()
    middleware_clock = clock or Clock()

    @app.post("/api/generate")
    def generate() -> dict[str, str]:
        return {"ok": "yes"}

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.add_middleware(
        InMemoryRateLimitMiddleware,
        requests_per_window=limit,
        window_seconds=window,
        trusted_proxies=trusted_proxies,
        clock=middleware_clock,
    )
    return app, TestClient(app), middleware_clock


def test_requests_beyond_the_limit_get_429() -> None:
    _, client, _ = build(limit=2)
    assert client.post("/api/generate").status_code == 200
    assert client.post("/api/generate").status_code == 200
    blocked = client.post("/api/generate")
    assert blocked.status_code == 429
    assert "Too many requests" in blocked.json()["detail"]


def test_unprotected_paths_and_preflight_are_not_limited() -> None:
    _, client, _ = build(limit=1)
    for _ in range(5):
        assert client.get("/health").status_code == 200
        assert client.options("/api/generate").status_code != 429


def test_window_expiry_allows_requests_again() -> None:
    _, client, clock = build(limit=1, window=60)
    assert client.post("/api/generate").status_code == 200
    assert client.post("/api/generate").status_code == 429
    clock.now += 61
    assert client.post("/api/generate").status_code == 200


def test_spoofed_forwarded_for_prefix_cannot_bypass_the_limit() -> None:
    # Regression: the first X-Forwarded-For entry is client-controlled, so rotating it
    # used to give every request a fresh bucket. The proxy appends the real address last.
    _, client, _ = build(limit=2, trusted_proxies=1)
    statuses = [
        client.post("/api/generate", headers={"X-Forwarded-For": f"10.0.0.{i}, 203.0.113.9"}).status_code
        for i in range(5)
    ]
    assert statuses == [200, 200, 429, 429, 429]


def test_different_real_clients_have_separate_limits() -> None:
    _, client, _ = build(limit=1, trusted_proxies=1)
    assert client.post("/api/generate", headers={"X-Forwarded-For": "203.0.113.1"}).status_code == 200
    assert client.post("/api/generate", headers={"X-Forwarded-For": "203.0.113.2"}).status_code == 200
    assert client.post("/api/generate", headers={"X-Forwarded-For": "203.0.113.1"}).status_code == 429


def test_header_is_ignored_when_no_proxy_is_trusted() -> None:
    _, client, _ = build(limit=1, trusted_proxies=0)
    assert client.post("/api/generate", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.post("/api/generate", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 429


def test_header_with_too_few_entries_falls_back_to_socket_address() -> None:
    _, client, _ = build(limit=1, trusted_proxies=2)
    assert client.post("/api/generate", headers={"X-Forwarded-For": "9.9.9.9"}).status_code == 200
    assert client.post("/api/generate", headers={"X-Forwarded-For": "8.8.8.8"}).status_code == 429


def test_stale_clients_are_swept_so_memory_does_not_grow() -> None:
    # Regression: buckets of clients that never returned were kept forever.
    app, client, clock = build(limit=5, window=60)
    client.get("/health")  # builds the middleware stack
    middleware = next(_middleware_instances(app))
    for i in range(20):
        client.post("/api/generate", headers={"X-Forwarded-For": f"198.51.100.{i}"})
    assert len(middleware.requests) == 20
    clock.now += 120
    client.post("/api/generate", headers={"X-Forwarded-For": "203.0.113.200"})
    assert len(middleware.requests) == 1


def _middleware_instances(app: FastAPI):
    stack = app.middleware_stack
    while stack is not None:
        if isinstance(stack, InMemoryRateLimitMiddleware):
            yield stack
            return
        stack = getattr(stack, "app", None)
    pytest.fail("rate limit middleware not found")
