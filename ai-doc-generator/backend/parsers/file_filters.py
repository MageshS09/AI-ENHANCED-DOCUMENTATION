"""Rules for selecting repository files to analyze."""

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
    """Return whether a path should be ignored during repository analysis."""
    return any(part in IGNORED_DIRS for part in path.parts)


def is_relevant_text_file(path: Path) -> bool:
    """Return whether a file is small enough and likely text."""
    if should_ignore_path(path) or not path.is_file():
        return False
    if path.stat().st_size > MAX_FILE_SIZE_BYTES:
        return False
    if path.name in {"Dockerfile", ".env.example"}:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS
