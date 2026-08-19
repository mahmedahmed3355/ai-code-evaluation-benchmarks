from __future__ import annotations

from scripts.error_tracking import ErrorTracker


class ValidationEventLogger:
    def __init__(self) -> None:
        self.tracker = ErrorTracker()

    def task_failed(
        self,
        task: str,
        reason: str,
    ) -> None:
        self.tracker.record(
            event="task_validation_failed",
            message=reason,
            metadata={
                "task": task,
            },
        )

    def task_passed(
        self,
        task: str,
    ) -> None:
        self.tracker.record(
            event="task_validation_passed",
            message="validation_success",
            metadata={
                "task": task,
            },
        )

    def report(self) -> dict:
        return self.tracker.to_dict()
