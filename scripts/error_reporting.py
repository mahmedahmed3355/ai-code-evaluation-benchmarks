from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from scripts.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationErrorReport:
    component: str
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def emit(self) -> None:
        logger.error(
            "validation_error_report component=%s errors=%d metadata=%s",
            self.component,
            len(self.errors),
            self.metadata,
        )


def report_validation_failure(
    component: str,
    errors: list[str],
    **metadata: Any,
) -> None:
    report = ValidationErrorReport(
        component=component,
        errors=errors,
        metadata={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **metadata,
        },
    )

    report.emit()
