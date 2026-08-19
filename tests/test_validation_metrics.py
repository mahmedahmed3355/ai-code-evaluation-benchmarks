from scripts.validation_metrics import ValidationMetrics


def test_empty_metrics_have_zero_success_rate():
    metrics = ValidationMetrics()

    assert metrics.total_tasks == 0
    assert metrics.passed_tasks == 0
    assert metrics.failed_tasks == 0
    assert metrics.success_rate == 0.0


def test_metrics_calculate_success_rate():
    metrics = ValidationMetrics(
        total_tasks=10,
        passed_tasks=8,
        failed_tasks=2,
    )

    assert metrics.success_rate == 80.0


def test_metrics_export_to_dictionary():
    metrics = ValidationMetrics(
        total_tasks=5,
        passed_tasks=4,
        failed_tasks=1,
    )

    data = metrics.to_dict()

    assert data["total_tasks"] == 5
    assert data["passed_tasks"] == 4
    assert data["failed_tasks"] == 1
    assert data["success_rate"] == 80.0
