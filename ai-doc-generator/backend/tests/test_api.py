"""HTTP-level tests for the generation endpoint (no network, no LLM)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api import routes
from main import app as main_app
from utils.exceptions import (
    ConfigurationError,
    LLMGenerationError,
    RepositoryCloneError,
)


@pytest.fixture
def client() -> TestClient:
    # A bare app with just the router avoids the production rate limiter, which would
    # otherwise count requests across tests.
    app = FastAPI()
    app.include_router(routes.router, prefix="/api")
    return TestClient(app, raise_server_exceptions=False)


def stub_generate(monkeypatch: pytest.MonkeyPatch, result=None, error: Exception | None = None):
    calls: list[str] = []

    async def fake(self, repository_url: str) -> str:
        calls.append(repository_url)
        if error:
            raise error
        return result

    monkeypatch.setattr(routes.DocumentationService, "__init__", lambda self: None)
    monkeypatch.setattr(routes.DocumentationService, "generate", fake)
    return calls


def test_health_endpoint() -> None:
    assert TestClient(main_app).get("/health").json() == {"status": "ok"}


def test_generate_returns_markdown(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = stub_generate(monkeypatch, result="# Title")
    response = client.post("/api/generate", json={"repository_url": "https://github.com/a/b"})
    assert response.status_code == 200
    assert response.json() == {"markdown": "# Title"}
    assert calls == ["https://github.com/a/b"]


@pytest.mark.parametrize("body", [{}, {"repository_url": "not a url"}, {"repository_url": 5}, {"repository_url": ""}])
def test_invalid_body_returns_422(client: TestClient, body: dict) -> None:
    assert client.post("/api/generate", json=body).status_code == 422


def test_non_github_host_returns_400_with_message(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    stub_generate(monkeypatch, error=ValueError("Only github.com repository URLs are supported."))
    response = client.post("/api/generate", json={"repository_url": "https://example.com/a/b"})
    assert response.status_code == 400
    assert "github.com" in response.json()["detail"]


@pytest.mark.parametrize(
    ("error", "status"),
    [
        (RepositoryCloneError(), 422),
        (ConfigurationError(), 500),
        (LLMGenerationError(), 502),
    ],
)
def test_expected_errors_map_to_their_status_codes(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, error: Exception, status: int
) -> None:
    stub_generate(monkeypatch, error=error)
    response = client.post("/api/generate", json={"repository_url": "https://github.com/a/b"})
    assert response.status_code == status
    assert response.json()["detail"] == error.public_message


def test_unexpected_errors_do_not_leak_details() -> None:
    # The production app registers the global handler; use it with a failing route.
    @main_app.get("/__boom")
    async def boom() -> None:
        raise RuntimeError("secret internal detail")

    response = TestClient(main_app, raise_server_exceptions=False).get("/__boom")
    assert response.status_code == 500
    assert "secret" not in response.text
