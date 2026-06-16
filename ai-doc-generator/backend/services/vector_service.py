"""FAISS embedding and retrieval service."""

import numpy as np
import faiss
from openai import AsyncOpenAI

from models.repository import FileSummary
from utils.config import get_settings
from utils.exceptions import ConfigurationError


class VectorService:
    """Create embeddings, store them in FAISS, and retrieve relevant context."""

    def __init__(self) -> None:
        """Initialize OpenAI client and settings."""
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.openai_api_key)

    async def retrieve_context(self, summaries: list[FileSummary], query: str, top_k: int = 12) -> list[FileSummary]:
        """Return the most relevant file summaries for a documentation query."""
        if not summaries:
            return []
        texts = [self._summary_text(summary) for summary in summaries]
        embeddings = await self._embed(texts)
        query_embedding = await self._embed([query])
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)
        _, indices = index.search(query_embedding, min(top_k, len(summaries)))
        return [summaries[index] for index in indices[0] if index >= 0]

    async def _embed(self, texts: list[str]) -> np.ndarray:
        """Create normalized embeddings for a list of text chunks."""
        if not self.settings.openai_api_key:
            raise ConfigurationError("OPENAI_API_KEY is required to generate documentation.")
        response = await self.client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        vectors = np.array([item.embedding for item in response.data], dtype="float32")
        faiss.normalize_L2(vectors)
        return vectors

    def _summary_text(self, summary: FileSummary) -> str:
        """Convert a file summary into text suitable for embeddings."""
        return f"{summary.path}\n{summary.language}\n{summary.summary}\n{summary.content_excerpt}"
