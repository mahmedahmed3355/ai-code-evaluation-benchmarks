import json
import logging

from scripts.logging_config import JsonFormatter


def test_json_formatter_outputs_structured_fields():
    formatter = JsonFormatter()

    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="validation_started",
        args=(),
        exc_info=None,
    )

    output = formatter.format(record)
    payload = json.loads(output)

    assert "timestamp" in payload
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.logger"
    assert payload["event"] == "validation_started"
