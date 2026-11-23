"""Tests for structured logging."""

import json
import logging

from utils.logging import JsonFormatter


def make_record(message: str = "hello", **extra) -> logging.LogRecord:
    logger = logging.getLogger("tests.logging")
    record = logger.makeRecord("tests.logging", logging.INFO, __file__, 1, message, (), None, extra=extra)
    return record


def test_output_is_valid_json_even_with_quotes() -> None:
    payload = json.loads(JsonFormatter().format(make_record('he said "hi"\nnext line')))
    assert payload["message"] == 'he said "hi"\nnext line'
    assert payload["level"] == "INFO"
    assert payload["logger"] == "tests.logging"


def test_extra_fields_are_included() -> None:
    # Regression: the old format string silently dropped everything passed via extra=.
    payload = json.loads(JsonFormatter().format(make_record(repository_url="https://github.com/a/b", count=3)))
    assert payload["repository_url"] == "https://github.com/a/b"
    assert payload["count"] == 3


def test_exceptions_are_serialized() -> None:
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        import sys

        record = logging.getLogger("t").makeRecord("t", logging.ERROR, __file__, 1, "failed", (), sys.exc_info())
    assert "RuntimeError: boom" in json.loads(JsonFormatter().format(record))["exception"]


def test_unserializable_extra_does_not_raise() -> None:
    payload = json.loads(JsonFormatter().format(make_record(obj=object())))
    assert "object" in payload["obj"]
