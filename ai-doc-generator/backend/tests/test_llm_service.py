"""Tests for the LLM service using a fake client (no network)."""

from types import SimpleNamespace

import httpx
import pytest
from openai import APIConnectionError, AuthenticationError

from models.repository import RepositoryMetadata
from services import llm_service
from utils.config import get_settings
from utils.exceptions import ConfigurationError, LLMGenerationError

METADATA = RepositoryMetadata(name="demo", url="https://github.com/a/demo", directory_tree="demo")


class FakeCompletions:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response, self.error, self.kwargs = response, error, None

    async def create(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return self.response


def reply(content, choices: bool = True):
    if not choices:
        return SimpleNamespace(choices=[])
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def service(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    get_settings.cache_clear()
    instance = llm_service.LLMService()
    yield instance
    get_settings.cache_clear()


def attach(service, completions: FakeCompletions) -> FakeCompletions:
    service._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return completions


async def test_returns_stripped_markdown_and_sends_prompt(service) -> None:
    completions = attach(service, FakeCompletions(reply("  # Demo\n")))
    assert await service.generate_readme(METADATA, []) == "# Demo"
    assert completions.kwargs["model"] == service.settings.groq_model
    assert completions.kwargs["messages"][1]["role"] == "user"
    assert "demo" in completions.kwargs["messages"][1]["content"]


@pytest.mark.parametrize("content", ["", "   \n", None])
async def test_empty_output_is_an_upstream_error_not_a_client_error(service, content) -> None:
    # Regression: this used to raise ValueError, which the API reported as HTTP 400.
    attach(service, FakeCompletions(reply(content)))
    with pytest.raises(LLMGenerationError):
        await service.generate_readme(METADATA, [])


async def test_response_without_choices_is_handled(service) -> None:
    attach(service, FakeCompletions(reply(None, choices=False)))
    with pytest.raises(LLMGenerationError):
        await service.generate_readme(METADATA, [])


async def test_provider_errors_become_llm_generation_error(service) -> None:
    request = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    errors = [
        APIConnectionError(request=request),
        AuthenticationError("bad key", response=httpx.Response(401, request=request), body=None),
    ]
    for error in errors:
        attach(service, FakeCompletions(error=error))
        with pytest.raises(LLMGenerationError) as info:
            await service.generate_readme(METADATA, [])
        assert info.value.status_code == 502
        assert "bad key" not in info.value.public_message


async def test_missing_api_key_raises_configuration_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "")
    get_settings.cache_clear()
    try:
        with pytest.raises(ConfigurationError):
            await llm_service.LLMService().generate_readme(METADATA, [])
    finally:
        get_settings.cache_clear()


def test_client_is_created_lazily_with_a_timeout(service) -> None:
    assert service._client is None
    client = service.client
    assert client.timeout == llm_service.REQUEST_TIMEOUT_SECONDS
    assert service.client is client
