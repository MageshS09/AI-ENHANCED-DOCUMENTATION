"""High-level README generation workflow."""

import asyncio

from models.repository import RepositoryMetadata
from parsers.repository_parser import RepositoryParser
from services.llm_service import LLMService
from services.repository_service import RepositoryService
from services.vector_service import VectorService
from utils.logging import get_logger

logger = get_logger(__name__)


class DocumentationService:
    """Coordinate clone, parse, retrieve, generate, and cleanup steps."""

    def __init__(self) -> None:
        """Initialize workflow dependencies."""
        self.repository_service = RepositoryService()
        self.parser = RepositoryParser()
        self.vector_service = VectorService()
        self.llm_service = LLMService()

    async def generate(self, repository_url: str) -> str:
        """Generate README Markdown for a repository URL."""
        logger.info("generation_started", extra={"repository_url": repository_url})
        metadata = await asyncio.to_thread(self._parse_repository, repository_url)
        context = await self.vector_service.retrieve_context(
            metadata.file_summaries,
            "README sections: overview features installation configuration usage API endpoints folder structure",
        )
        markdown = await self.llm_service.generate_readme(metadata, context)
        logger.info("generation_completed", extra={"repository_url": repository_url})
        return markdown

    def _parse_repository(self, repository_url: str) -> RepositoryMetadata:
        """Clone and parse a repository in a worker thread."""
        with self.repository_service.clone(repository_url) as repo_path:
            return self.parser.parse(repo_path, repository_url)
