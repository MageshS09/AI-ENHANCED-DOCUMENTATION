"""Groq README generation service."""

from openai import AsyncOpenAI

from models.repository import FileSummary, RepositoryMetadata
from prompts.readme_prompt import build_readme_prompt
from utils.config import get_settings
from utils.exceptions import ConfigurationError


class LLMService:
    """Generate documentation using Groq's OpenAI-compatible chat completions API."""

    def __init__(self) -> None:
        """Initialize Groq client and settings."""
        self.settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=self.settings.groq_api_key,
            base_url=self.settings.groq_base_url,
        )

    async def generate_readme(
        self,
        metadata: RepositoryMetadata,
        context: list[FileSummary],
    ) -> str:
        """Generate README Markdown from repository context."""
        if not self.settings.groq_api_key:
            raise ConfigurationError("GROQ_API_KEY is required to generate documentation.")
        prompt = build_readme_prompt(metadata, context)
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
        markdown = (response.choices[0].message.content or "").strip()
        if not markdown:
            raise ValueError("Groq returned an empty README.")
        return markdown
