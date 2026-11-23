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


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("http://github.com/a/b", "https://github.com/a/b.git"),
        ("https://github.com/a/b.git", "https://github.com/a/b.git"),
        ("https://GitHub.com/a/b/tree/main/src", "https://github.com/a/b.git"),
        ("https://github.com/a/b/", "https://github.com/a/b.git"),
        ("https://github.com/some-org/my_repo.v2", "https://github.com/some-org/my_repo.v2.git"),
    ],
)
def test_accepts_common_url_shapes(url: str, expected: str) -> None:
    assert normalize_github_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "ftp://github.com/a/b",
        "https://github.com/onlyowner",
        "https://github.com/",
        "https://www.github.com/a/b",
        "https://user@github.com/a/b",
        "https://github.com.evil.com/a/b",
        "not a url",
    ],
)
def test_rejects_unsupported_urls(url: str) -> None:
    with pytest.raises(ValueError):
        normalize_github_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/a/..",
        "https://github.com/a/.",
        "https://github.com/a/b c",
        "https://github.com/-bad/x",
        "https://github.com/a/.git",
        "https://github.com/" + "o" * 40 + "/x",
    ],
)
def test_rejects_invalid_owner_or_repo_names(url: str) -> None:
    # Regression: names were never checked, so ".." produced a bogus clone URL.
    with pytest.raises(ValueError, match="invalid owner or repository"):
        normalize_github_url(url)
