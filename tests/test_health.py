import json

import scripts.health as health
from scripts.health import health_status
from scripts.validation_runtime import reset_validation_runtime


def test_health_status_reports_healthy_component() -> None:
    reset_validation_runtime()

    result = health_status()

    assert result["status"] == "healthy"
    assert result["component"] == "benchmark-validation-tooling"

    metrics = result["metrics"]

    assert isinstance(metrics, dict)
    assert metrics["total"] == 0
    assert metrics["passed"] == 0
    assert metrics["failed"] == 0

    errors = result["error_tracking"]

    assert isinstance(errors, dict)
    assert errors["count"] == 0


def test_health_status_exposes_runtime_errors() -> None:
    runtime = reset_validation_runtime()

    runtime.record_failure(
        event="validation_failed",
        message="missing_task_file",
        metadata={"task": "demo"},
    )

    result = health_status()

    assert result["metrics"]["failed"] == 1
    assert result["error_tracking"]["count"] == 1


def test_main_prints_json_health_status(
    capsys,
) -> None:
    reset_validation_runtime()

    assert health.main() == 0

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    assert result["status"] == "healthy"
    assert result["component"] == "benchmark-validation-tooling"
    assert result["metrics"]["total"] == 0
    assert result["error_tracking"]["count"] == 0
