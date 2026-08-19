#!/usr/bin/env python3

from pathlib import Path

from scripts.logging_config import get_logger
from scripts.validation_metrics import ValidationMetrics

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

    metrics = ValidationMetrics()
    failed = []

    print(f"Found {len(task_files)} tasks\n")

    for task_toml in task_files:
        task_dir = task_toml.parent
        missing = []

        for required in REQUIRED_FILES:
            if not (task_dir / required).is_file():
                missing.append(required)

        if missing:
            metrics.record_failure()
            failed.append((task_dir.relative_to(ROOT), missing))

            print(f"FAIL: {task_dir.relative_to(ROOT)}")

            for item in missing:
                print(f"  missing: {item}")

        else:
            metrics.record_success()
            print(f"PASS: {task_dir.relative_to(ROOT)}")

    print()

    print(
        "Validation metrics: "
        f"total={metrics.total}, "
        f"passed={metrics.passed}, "
        f"failed={metrics.failed}, "
        f"success_rate={metrics.success_rate:.2%}"
    )

    if failed:
        print(f"\nValidation failed: {len(failed)} task(s) have missing files.")
        return 1

    print(f"\nSUCCESS: All {len(task_files)} tasks have the required structure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
