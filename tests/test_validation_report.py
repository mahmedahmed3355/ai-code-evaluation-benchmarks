from typing import cast

import scripts.validation_report as validation_report
from scripts.validation_metrics import ValidationMetrics
from scripts.validation_report import build_validation_report


def test_validation_report_success_state() -> None:
    metrics = ValidationMetrics()

    metrics.record_success()
    metrics.record_success()

    report = build_validation_report(metrics)

    assert report["status"] == "success"

    tasks = cast(dict[str, int | float], report["tasks"])

    assert tasks["total"] == 2
    assert tasks["passed"] == 2
    assert tasks["failed"] == 0

    observability = cast(dict[str, object], report["observability"])

    assert observability["health"] == "healthy"
    assert observability["errors"] == 0
    assert observability["events"] == {}


def test_validation_report_failed_state_with_events() -> None:
    metrics = ValidationMetrics()

    metrics.record_success()
    metrics.record_failure()

    events: dict[str, object] = {
        "validation_started": 1,
        "validation_failed": 1,
    }

    report = build_validation_report(
        metrics,
        errors=2,
        events=events,
    )

    assert report["status"] == "failed"

    tasks = cast(dict[str, int | float], report["tasks"])

    assert tasks["total"] == 2
    assert tasks["passed"] == 1
    assert tasks["failed"] == 1

    observability = cast(dict[str, object], report["observability"])

    assert observability["health"] == "healthy"
    assert observability["errors"] == 2
    assert observability["events"] == events


def test_main_prints_json_report(
    capsys,
    monkeypatch,
) -> None:
    assert validation_report.main() == 0

    captured = capsys.readouterr()

    assert '"status": "success"' in captured.out
    assert '"health": "healthy"' in captured.out
