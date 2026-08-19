from typing import cast

from scripts.validation_metrics import ValidationMetrics
from scripts.validation_report import build_validation_report


def test_validation_report_success_state():
    metrics = ValidationMetrics()

    metrics.record_success()
    metrics.record_success()

    report = build_validation_report(metrics)

    assert report["status"] == "success"

    tasks = cast(dict[str, int | float], report["tasks"])

    assert tasks["total"] == 2
    assert tasks["passed"] == 2
    assert tasks["failed"] == 0

    observability = cast(dict[str, str | int], report["observability"])

    assert observability["health"] == "healthy"
    assert observability["errors"] == 0
