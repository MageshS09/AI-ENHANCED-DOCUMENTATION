"""OpenAI README generation service."""

from openai import AsyncOpenAI

from models.repository import FileSummary, RepositoryMetadata
from prompts.readme_prompt import build_readme_prompt
from utils.config import get_settings
from utils.exceptions import ConfigurationError


class LLMService:
    """Generate documentation using the OpenAI Responses API."""

    def __init__(self) -> None:
        """Initialize OpenAI client and settings."""
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def generate_readme(
        self,
        metadata: RepositoryMetadata,
        context: list[FileSummary],
    ) -> str:
        """Generate README Markdown from repository context."""
        if not self.settings.openai_api_key:
            raise ConfigurationError("OPENAI_API_KEY is required to generate documentation.")
        prompt = build_readme_prompt(metadata, context)
        response = await self.client.responses.create(
            model=self.settings.openai_model,
            input=[
                {
                    "role": "developer",
                    "content": "You write concise, accurate, production-ready README.md files.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        markdown = getattr(response, "output_text", "").strip()
        if not markdown:
            raise ValueError("OpenAI returned an empty README.")
        return markdown
