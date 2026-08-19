from scripts.error_tracking import ErrorTracker


def test_error_tracker_records_events():
    tracker = ErrorTracker()

    tracker.record(
        event="validation_failed",
        message="missing_task_file",
        metadata={"task": "demo"},
    )

    result = tracker.to_dict()

    assert result["count"] == 1
    assert result["errors"][0]["event"] == "validation_failed"
    assert result["errors"][0]["metadata"]["task"] == "demo"
