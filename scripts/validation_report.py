from __future__ import annotations

import json

from scripts.validation_runtime import ValidationRuntime, get_validation_runtime


def build_validation_report(
    runtime: ValidationRuntime | None = None,
    events: dict[str, object] | None = None,
) -> dict[str, object]:
    active_runtime = runtime or get_validation_runtime()

    metrics = active_runtime.metrics.to_dict()
    errors = active_runtime.errors.to_dict()

    return {
        "status": "success" if errors["count"] == 0 else "failed",
        "tasks": metrics,
        "observability": {
            "health": "healthy",
            "error_tracking": errors,
            "events": events or {},
        },
    }


def main() -> int:
    print(
        json.dumps(
            build_validation_report(),
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
