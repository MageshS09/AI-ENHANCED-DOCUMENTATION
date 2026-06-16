"""Input validation helpers."""

from urllib.parse import urlparse


def normalize_github_url(url: str) -> str:
    """Validate and normalize a public GitHub repository URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Repository URL must use http or https.")
    if parsed.netloc.lower() != "github.com":
        raise ValueError("Only github.com repository URLs are supported.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("Repository URL must include an owner and repository name.")

    owner, repo = parts[0], parts[1].removesuffix(".git")
    return f"https://github.com/{owner}/{repo}.git"
