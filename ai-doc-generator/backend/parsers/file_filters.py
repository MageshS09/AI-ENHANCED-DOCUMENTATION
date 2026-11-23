"""Rules for selecting repository files to analyze.

Cloned repositories are untrusted input. A repository can contain symlinks that
point outside the checkout (for example ``README.md -> /app/.env``), so every
read goes through :func:`safe_read_text`, which refuses symlinks and any path
that resolves outside the repository root.
"""

import os
from collections.abc import Iterator
from pathlib import Path

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".next",
    ".venv",
    "venv",
    "coverage",
}
MAX_FILE_SIZE_BYTES = 1_000_000
# Upper bound on files inspected per repository, so huge repositories cannot
# make a single request read an unbounded amount of data.
MAX_FILES_SCANNED = 2_000
TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".env",
    ".example",
    ".html",
    ".css",
    ".scss",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".cs",
    ".sh",
    ".sql",
}


def should_ignore_path(path: Path) -> bool:
    """Return whether a path (relative to the repository root) should be ignored."""
    return any(part in IGNORED_DIRS for part in path.parts)


def is_safe_file(path: Path, root: Path) -> bool:
    """Return whether ``path`` is a regular file located inside ``root``.

    Symlinks are rejected outright, and the resolved path must stay within the
    resolved root, which also covers files reached through a symlinked directory.
    """
    try:
        if path.is_symlink() or not path.is_file():
            return False
        path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    return True


def safe_read_text(path: Path, root: Path, limit: int | None = None) -> str | None:
    """Read a text file from the repository, or return ``None`` if it is unsafe or unreadable."""
    if not is_safe_file(path, root):
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return text[:limit] if limit is not None else text


def is_relevant_text_file(path: Path, root: Path) -> bool:
    """Return whether a file is small enough, safe to read and likely text."""
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    # Only the path inside the repository matters: a temp directory or a
    # repository that happens to be named "build" must not hide every file.
    if should_ignore_path(relative) or not is_safe_file(path, root):
        return False
    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return False
    if path.name in {"Dockerfile", ".env.example"}:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def iter_relevant_files(root: Path, limit: int = MAX_FILES_SCANNED) -> Iterator[Path]:
    """Yield relevant files in a deterministic order, without entering ignored directories.

    Walking with pruning (instead of ``rglob``) avoids traversing ``node_modules``
    and similar trees, and symlinked directories are never followed.
    """
    yielded = 0
    for current, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name not in IGNORED_DIRS)
        for name in sorted(filenames):
            path = Path(current) / name
            if is_relevant_text_file(path, root):
                yield path
                yielded += 1
                if yielded >= limit:
                    return
