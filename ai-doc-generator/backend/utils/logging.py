"""Structured logging configuration."""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure JSON-like structured application logging."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='{"level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module logger."""
    return logging.getLogger(name)
