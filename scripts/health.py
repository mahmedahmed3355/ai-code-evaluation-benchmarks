from __future__ import annotations

import json

from scripts.validation_metrics import ValidationMetrics


def health_status() -> dict[str, object]:
    metrics = ValidationMetrics()

    return {
        "status": "healthy",
        "component": "benchmark-validation-tooling",
        "metrics": metrics.to_dict(),
    }


def main() -> int:
    print(
        json.dumps(
            health_status(),
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
