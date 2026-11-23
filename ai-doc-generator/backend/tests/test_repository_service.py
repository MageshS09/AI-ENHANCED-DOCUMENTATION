"""Tests for cloning, using a fake Repo.clone_from (no network)."""

from pathlib import Path

import pytest
from git import GitCommandError

from services import repository_service
from services.repository_service import RepositoryService
from utils.exceptions import RepositoryCloneError


def test_clone_uses_normalized_url_shallow_and_no_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: dict = {}

    def fake_clone(url, destination, **kwargs):
        seen.update(url=url, destination=Path(destination), kwargs=kwargs)
        Path(destination).mkdir(parents=True)

    monkeypatch.setattr(repository_service.Repo, "clone_from", fake_clone)
    with RepositoryService().clone("https://github.com/a/b") as path:
        assert path.exists() and path.name == "b"
    assert seen["url"] == "https://github.com/a/b.git"
    assert seen["kwargs"]["multi_options"] == ["--depth=1"]
    assert seen["kwargs"]["env"]["GIT_TERMINAL_PROMPT"] == "0"


def test_temporary_directory_is_removed_afterwards(monkeypatch: pytest.MonkeyPatch) -> None:
    created: list[Path] = []

    def fake_clone(url, destination, **kwargs):
        Path(destination).mkdir(parents=True)
        created.append(Path(destination))

    monkeypatch.setattr(repository_service.Repo, "clone_from", fake_clone)
    with RepositoryService().clone("https://github.com/a/b"):
        pass
    assert not created[0].exists()


def test_clone_failure_becomes_repository_clone_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def failing_clone(*args, **kwargs):
        raise GitCommandError("clone", 128)

    monkeypatch.setattr(repository_service.Repo, "clone_from", failing_clone)
    with pytest.raises(RepositoryCloneError) as info, RepositoryService().clone("https://github.com/a/b"):
        pass
    assert info.value.status_code == 422


def test_invalid_url_is_rejected_before_cloning(monkeypatch: pytest.MonkeyPatch) -> None:
    def must_not_run(*args, **kwargs):
        raise AssertionError("clone should not be attempted")

    monkeypatch.setattr(repository_service.Repo, "clone_from", must_not_run)
    with pytest.raises(ValueError), RepositoryService().clone("https://github.com/a/.."):
        pass
