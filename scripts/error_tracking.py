from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class ErrorTracker:
    errors: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        event: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.errors.append(
            {
                "event": event,
                "message": message,
                "metadata": metadata or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    @property
    def count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "errors": self.errors,
            "count": self.count,
        }
