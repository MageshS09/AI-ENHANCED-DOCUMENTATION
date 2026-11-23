"""Input validation helpers."""

import re
from urllib.parse import urlparse

# GitHub owners are alphanumeric with single hyphens; repository names may also
# contain dots and underscores. "." and ".." are never valid repository names.
_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_REPO_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,100}$")


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
    if not _OWNER_PATTERN.fullmatch(owner) or repo in {".", ".."} or not _REPO_PATTERN.fullmatch(repo):
        raise ValueError("Repository URL contains an invalid owner or repository name.")
    return f"https://github.com/{owner}/{repo}.git"
