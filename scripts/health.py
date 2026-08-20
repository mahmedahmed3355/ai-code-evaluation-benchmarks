from __future__ import annotations

import json
from typing import Any

from scripts.validation_runtime import get_validation_runtime


def health_status() -> dict[str, Any]:
    runtime = get_validation_runtime()

    return {
        "status": "healthy",
        "component": "benchmark-validation-tooling",
        "metrics": runtime.metrics.to_dict(),
        "error_tracking": runtime.errors.to_dict(),
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
