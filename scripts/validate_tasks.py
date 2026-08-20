#!/usr/bin/env python3

import json
from pathlib import Path

from scripts.logging_config import get_logger
from scripts.validation_events import ValidationEventLogger
from scripts.validation_metrics import ValidationMetrics
from scripts.validation_report import build_validation_report
from scripts.validation_runtime import ValidationRuntime

ROOT = Path(__file__).resolve().parents[1]

logger = get_logger(__name__)

REQUIRED_FILES = [
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
    "tests/test_outputs.py",
]


def task_dirs():
    """Yield directories containing benchmark task definitions."""
    for task_file in sorted(ROOT.rglob("task.toml")):
        yield task_file.parent


def main() -> int:
    task_files = sorted(ROOT.glob("*/*/task.toml"))

    if not task_files:
        print("ERROR: No tasks found.")
        return 1

    runtime = ValidationRuntime()
    events = ValidationEventLogger()

    print(f"Found {len(task_files)} tasks\n")

    for task_toml in task_files:
        task_dir = task_toml.parent
        missing = []
        task_name = str(task_dir.relative_to(ROOT))

        for required in REQUIRED_FILES:
            if not (task_dir / required).is_file():
                missing.append(required)

        if missing:
            runtime.record_failure(
                event="missing_required_files",
                message="benchmark task is missing required files",
                metadata={
                    "task": task_name,
                    "missing": missing,
                },
            )

            events.task_failed(
                task_name,
                "missing_required_files",
            )

            print(f"FAIL: {task_name}")

            for item in missing:
                print(f"  missing: {item}")

        else:
            runtime.record_success()

            events.task_passed(task_name)

            print(f"PASS: {task_name}")

    metrics: ValidationMetrics = runtime.metrics

    print()

    print(
        "Validation metrics: "
        f"total={metrics.total}, "
        f"passed={metrics.passed}, "
        f"failed={metrics.failed}, "
        f"success_rate={metrics.success_rate:.2%}"
    )

    report = build_validation_report(
        runtime,
        events=events.report(),
    )

    print("\nValidation observability report:")
    print(json.dumps(report, indent=2))

    if metrics.failed:
        print(
            f"\nValidation failed: "
            f"{metrics.failed} task(s) have missing files."
        )
        return 1

    print(f"\nSUCCESS: All {len(task_files)} tasks have the required structure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
