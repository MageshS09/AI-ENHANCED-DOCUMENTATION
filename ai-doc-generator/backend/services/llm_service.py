"""Groq README generation service."""

from openai import AsyncOpenAI, OpenAIError

from models.repository import FileSummary, RepositoryMetadata
from prompts.readme_prompt import build_readme_prompt
from utils.config import get_settings
from utils.exceptions import ConfigurationError, LLMGenerationError
from utils.logging import get_logger

logger = get_logger(__name__)
REQUEST_TIMEOUT_SECONDS = 60.0


class LLMService:
    """Generate documentation using Groq's OpenAI-compatible chat completions API."""

    def __init__(self) -> None:
        """Load settings; the API client is created lazily once a key is known to exist."""
        self.settings = get_settings()
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Return the Groq client, creating it on first use.

        Creating it eagerly made the SDK raise "Missing credentials" whenever
        GROQ_API_KEY was unset, hiding the clearer ConfigurationError below.
        """
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self.settings.groq_api_key,
                base_url=self.settings.groq_base_url,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        return self._client

    async def generate_readme(
        self,
        metadata: RepositoryMetadata,
        context: list[FileSummary],
    ) -> str:
        """Generate README Markdown from repository context."""
        if not self.settings.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY is required to generate documentation.")
        prompt = build_readme_prompt(metadata, context)
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You write concise, accurate, production-ready README.md files.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
        except OpenAIError as exc:
            # Provider errors (auth, rate limit, timeout, outage) are upstream failures, not bad requests.
            logger.error("llm_request_failed", extra={"error_type": type(exc).__name__})
            raise LLMGenerationError() from exc
        message = response.choices[0].message.content if response.choices else None
        markdown = (message or "").strip()
        if not markdown:
            raise LLMGenerationError("The language model returned an empty README. Please try again.")
        return markdown
