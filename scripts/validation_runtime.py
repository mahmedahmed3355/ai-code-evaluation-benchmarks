from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from scripts.error_tracking import ErrorTracker
from scripts.validation_metrics import ValidationMetrics


@dataclass
class ValidationRuntime:
    """Shared in-process state for benchmark validation observability."""

    metrics: ValidationMetrics = field(default_factory=ValidationMetrics)
    errors: ErrorTracker = field(default_factory=ErrorTracker)

    def record_success(self) -> None:
        self.metrics.record_success()

    def record_failure(
        self,
        event: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.metrics.record_failure()
        self.errors.record(
            event=event,
            message=message,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "metrics": self.metrics.to_dict(),
            "errors": self.errors.to_dict(),
        }


_runtime = ValidationRuntime()


def get_validation_runtime() -> ValidationRuntime:
    return _runtime


def reset_validation_runtime() -> ValidationRuntime:
    global _runtime
    _runtime = ValidationRuntime()
    return _runtime
