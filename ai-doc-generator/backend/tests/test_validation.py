"""Validation tests."""

import pytest

from utils.validation import normalize_github_url


def test_normalize_github_url() -> None:
    """It normalizes supported GitHub URLs to clone URLs."""
    assert normalize_github_url("https://github.com/openai/openai-python") == (
        "https://github.com/openai/openai-python.git"
    )


def test_rejects_non_github_url() -> None:
    """It rejects unsupported hosts."""
    with pytest.raises(ValueError, match="Only github.com"):
        normalize_github_url("https://example.com/org/repo")
