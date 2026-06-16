"""Repository cloning and cleanup."""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from git import GitCommandError
from git import Repo

from utils.exceptions import RepositoryCloneError
from utils.validation import normalize_github_url


class RepositoryService:
    """Clone public GitHub repositories into temporary directories."""

    @contextmanager
    def clone(self, repository_url: str) -> Iterator[Path]:
        """Clone a repository and delete temporary files afterwards."""
        clone_url = normalize_github_url(repository_url)
        with tempfile.TemporaryDirectory(prefix="ai-doc-generator-") as tmpdir:
            destination = Path(tmpdir) / clone_url.rstrip("/").split("/")[-1].removesuffix(".git")
            try:
                Repo.clone_from(clone_url, destination, multi_options=["--depth=1"])
            except GitCommandError as exc:
                raise RepositoryCloneError() from exc
            yield destination
