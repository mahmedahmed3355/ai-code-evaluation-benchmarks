from __future__ import annotations

import json

from scripts.validation_metrics import ValidationMetrics


def build_validation_report(
    metrics: ValidationMetrics,
    errors: int = 0,
    events: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "status": "success" if errors == 0 else "failed",
        "tasks": metrics.to_dict(),
        "observability": {
            "health": "healthy",
            "errors": errors,
            "events": events or {},
        },
    }


def main() -> int:
    metrics = ValidationMetrics()

    print(
        json.dumps(
            build_validation_report(metrics),
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
