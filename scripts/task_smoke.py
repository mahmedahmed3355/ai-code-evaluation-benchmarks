from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from scripts.logging_config import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]


def run_command(command: list[str], cwd: Path) -> bool:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error(
            "command_failed command=%s stderr=%s",
            " ".join(command),
            result.stderr,
        )
        return False

    return True


def smoke_task(task: Path) -> bool:
    try:
        task_name = str(task.relative_to(ROOT))
    except ValueError:
        task_name = str(task)

    logger.info(
        "task_smoke_start task=%s",
        task_name,
    )

    required = [
        task / "environment" / "Dockerfile",
        task / "tests" / "Dockerfile",
        task / "solution" / "solve.sh",
        task / "tests" / "test.sh",
    ]

    for item in required:
        if not item.exists():
            logger.error(
                "missing_task_asset asset=%s",
                item,
            )
            return False

    logger.info(
        "task_smoke_pass task=%s",
        task_name,
    )

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run benchmark task smoke validation."
    )

    parser.add_argument(
        "--task",
        required=True,
        help="Task path relative to repository root.",
    )

    args = parser.parse_args()

    task = ROOT / args.task

    if not task.exists():
        logger.error("task_not_found task=%s", args.task)
        return 1

    return 0 if smoke_task(task) else 1


if __name__ == "__main__":
    raise SystemExit(main())
