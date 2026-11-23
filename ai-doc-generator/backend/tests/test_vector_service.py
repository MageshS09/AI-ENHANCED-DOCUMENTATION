"""Tests for TF-IDF retrieval."""

from models.repository import FileSummary
from services.vector_service import VectorService


def summary(path: str, text: str) -> FileSummary:
    return FileSummary(path=path, language="py", summary=text, content_excerpt=text)


async def test_empty_input_returns_empty_list() -> None:
    assert await VectorService().retrieve_context([], "anything") == []


async def test_most_relevant_file_ranks_first() -> None:
    items = [
        summary("a.py", "database migration schema tables"),
        summary("b.py", "installation configuration environment variables usage"),
        summary("c.py", "image resize thumbnail"),
    ]
    ranked = await VectorService().retrieve_context(items, "installation configuration usage")
    assert ranked[0].path == "b.py"


async def test_top_k_limits_results_and_never_exceeds_input() -> None:
    items = [summary(f"{i}.py", f"word{i} shared") for i in range(5)]
    assert len(await VectorService().retrieve_context(items, "shared", top_k=2)) == 2
    assert len(await VectorService().retrieve_context(items, "shared", top_k=50)) == 5


async def test_query_without_matching_terms_still_returns_results() -> None:
    items = [summary("a.py", "alpha"), summary("b.py", "beta")]
    assert len(await VectorService().retrieve_context(items, "zzz")) == 2


def test_cosine_similarity_edge_cases() -> None:
    service = VectorService()
    assert service._cosine_similarity({}, {"a": 1.0}) == 0.0
    assert service._cosine_similarity({"a": 0.0}, {"a": 1.0}) == 0.0
    assert abs(service._cosine_similarity({"a": 1.0}, {"a": 2.0}) - 1.0) < 1e-9
