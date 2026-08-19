from scripts.validation_metrics import ValidationMetrics


def test_empty_metrics_have_zero_success_rate():
    metrics = ValidationMetrics()

    assert metrics.total == 0
    assert metrics.passed == 0
    assert metrics.failed == 0
    assert metrics.success_rate == 0.0


def test_metrics_calculate_success_rate():
    metrics = ValidationMetrics()

    metrics.record_success()
    metrics.record_success()
    metrics.record_failure()

    assert metrics.total == 3
    assert metrics.passed == 2
    assert metrics.failed == 1
    assert metrics.success_rate == 2 / 3


def test_metrics_export_to_dictionary():
    metrics = ValidationMetrics()

    metrics.record_success()
    metrics.record_failure()

    assert metrics.to_dict() == {
        "total": 2,
        "passed": 1,
        "failed": 1,
        "success_rate": 0.5,
    }
