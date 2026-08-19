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

def test_get_logger_emits_structured_json(capsys):
    import json
    from uuid import uuid4

    from scripts.logging_config import get_logger

    logger_name = f"test.structured.{uuid4().hex}"
    logger = get_logger(logger_name)

    logger.info("task_isolation_pass task=sample-task")

    captured = capsys.readouterr()

    assert captured.out.strip()

    payload = json.loads(captured.out.strip())

    assert payload["level"] == "INFO"
    assert payload["logger"] == logger_name
    assert payload["event"] == (
        "task_isolation_pass task=sample-task"
    )
    assert "timestamp" in payload
