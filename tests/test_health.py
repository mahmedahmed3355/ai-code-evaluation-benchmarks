from typing import cast

from scripts.health import health_status


def test_health_status_reports_healthy_component():
    result = health_status()

    assert result["status"] == "healthy"
    assert result["component"] == "benchmark-validation-tooling"

    metrics = cast(dict[str, int | float], result["metrics"])

    assert metrics["total"] == 0
    assert metrics["passed"] == 0
    assert metrics["failed"] == 0
