"""Local TF-IDF retrieval service (no external API required)."""

import math
import re
from collections import Counter

from models.repository import FileSummary

_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


class VectorService:
    """Rank file summaries against a query using TF-IDF cosine similarity."""

    async def retrieve_context(self, summaries: list[FileSummary], query: str, top_k: int = 12) -> list[FileSummary]:
        """Return the most relevant file summaries for a documentation query."""
        if not summaries:
            return []
        documents = [self._tokenize(self._summary_text(summary)) for summary in summaries]
        query_tokens = self._tokenize(query)

        idf = self._compute_idf(documents)
        doc_vectors = [self._tfidf_vector(doc, idf) for doc in documents]
        query_vector = self._tfidf_vector(query_tokens, idf)

        scored = [
            (self._cosine_similarity(query_vector, doc_vector), index)
            for index, doc_vector in enumerate(doc_vectors)
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        top_indices = [index for _, index in scored[: min(top_k, len(summaries))]]
        return [summaries[index] for index in top_indices]

    def _summary_text(self, summary: FileSummary) -> str:
        """Convert a file summary into text suitable for ranking."""
        return f"{summary.path}\n{summary.language}\n{summary.summary}\n{summary.content_excerpt}"

    def _tokenize(self, text: str) -> list[str]:
        """Lowercase and split text into alphanumeric tokens."""
        return _TOKEN_PATTERN.findall(text.lower())

    def _compute_idf(self, documents: list[list[str]]) -> dict[str, float]:
        """Compute inverse document frequency across all documents."""
        doc_count = len(documents)
        term_doc_counts: Counter[str] = Counter()
        for tokens in documents:
            term_doc_counts.update(set(tokens))
        return {
            term: math.log((1 + doc_count) / (1 + count)) + 1.0
            for term, count in term_doc_counts.items()
        }

    def _tfidf_vector(self, tokens: list[str], idf: dict[str, float]) -> dict[str, float]:
        """Build a sparse TF-IDF vector for a token list."""
        if not tokens:
            return {}
        term_counts = Counter(tokens)
        return {
            term: (count / len(tokens)) * idf.get(term, 0.0)
            for term, count in term_counts.items()
        }

    def _cosine_similarity(self, vector_a: dict[str, float], vector_b: dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors."""
        if not vector_a or not vector_b:
            return 0.0
        shared_terms = vector_a.keys() & vector_b.keys()
        dot_product = sum(vector_a[term] * vector_b[term] for term in shared_terms)
        norm_a = math.sqrt(sum(value * value for value in vector_a.values()))
        norm_b = math.sqrt(sum(value * value for value in vector_b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
