from scripts.validation_runtime import (
    get_validation_runtime,
    reset_validation_runtime,
)


def test_runtime_records_success_and_failure() -> None:
    runtime = reset_validation_runtime()

    runtime.record_success()

    runtime.record_failure(
        event="validation_failed",
        message="missing_task_file",
        metadata={"task": "demo"},
    )

    result = runtime.to_dict()

    assert result["metrics"]["total"] == 2
    assert result["metrics"]["passed"] == 1
    assert result["metrics"]["failed"] == 1

    assert result["errors"]["count"] == 1
    assert result["errors"]["errors"][0]["event"] == "validation_failed"


def test_runtime_singleton_can_be_accessed() -> None:
    runtime = reset_validation_runtime()

    assert get_validation_runtime() is runtime
