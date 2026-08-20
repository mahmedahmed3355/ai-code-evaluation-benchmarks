import json

import scripts.health as health
from scripts.health import health_status


def test_health_status_reports_healthy_component() -> None:
    result = health_status()

    assert result["status"] == "healthy"
    assert result["component"] == "benchmark-validation-tooling"

    metrics = result["metrics"]

    assert isinstance(metrics, dict)
    assert metrics["total"] == 0
    assert metrics["passed"] == 0
    assert metrics["failed"] == 0


def test_main_prints_json_health_status(
    capsys,
) -> None:
    assert health.main() == 0

    captured = capsys.readouterr()

    result = json.loads(captured.out)

    assert result["status"] == "healthy"
    assert result["component"] == "benchmark-validation-tooling"
    assert result["metrics"]["total"] == 0
