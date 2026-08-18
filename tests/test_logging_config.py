import json
import logging

from scripts.logging_config import get_logger


def test_get_logger_returns_configured_logger():
    logger = get_logger("benchmark-test")

    assert isinstance(logger, logging.Logger)
    assert logger.handlers


def test_logger_uses_json_formatter():
    logger = get_logger("benchmark-json-test")

    formatter = logger.handlers[0].formatter

    assert formatter is not None

    record = logging.LogRecord(
        name="benchmark-json-test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="validation_completed",
        args=(),
        exc_info=None,
    )

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["event"] == "validation_completed"
    assert "timestamp" in payload
