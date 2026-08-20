from scripts.validation_report import build_validation_report
from scripts.validation_runtime import reset_validation_runtime


def test_validation_report_is_successful_without_errors() -> None:
    runtime = reset_validation_runtime()

    report = build_validation_report(runtime)

    assert report["status"] == "success"
    assert report["tasks"]["total"] == 0
    assert report["observability"]["error_tracking"]["count"] == 0


def test_validation_report_includes_tracked_failures() -> None:
    runtime = reset_validation_runtime()

    runtime.record_failure(
        event="task_validation_failed",
        message="invalid_manifest",
        metadata={"task": "demo"},
    )

    report = build_validation_report(runtime)

    assert report["status"] == "failed"
    assert report["tasks"]["failed"] == 1

    errors = report["observability"]["error_tracking"]

    assert errors["count"] == 1
    assert errors["errors"][0]["event"] == "task_validation_failed"
