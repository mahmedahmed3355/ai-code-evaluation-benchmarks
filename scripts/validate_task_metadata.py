from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from scripts.logging_config import get_logger

ROOT = Path(__file__).resolve().parents[1]
logger = get_logger(__name__)


def task_directories(root: Path = ROOT) -> list[Path]:
    return sorted(
        task_file.parent
        for task_file in root.rglob("task.toml")
        if ".git" not in task_file.parts
    )


def load_task_metadata(task_dir: Path) -> dict[str, Any]:
    task_file = task_dir / "task.toml"

    with task_file.open("rb") as handle:
        data: dict[str, Any] = tomllib.load(handle)

    return data


def positive_number(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and value > 0
    )


def non_negative_number(value: Any) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and value >= 0
    )


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_modern_schema(
    task_dir: Path,
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    task = data["task"]

    if not isinstance(task, dict):
        return [f"{task_dir}: [task] section must be a table"]

    if not non_empty_string(task.get("name")):
        errors.append(f"{task_dir}: task.name must be a non-empty string")

    if not non_empty_string(task.get("description")):
        errors.append(
            f"{task_dir}: task.description must be a non-empty string"
        )

    authors = task.get("authors")
    metadata = data.get("metadata")

    has_task_authors = isinstance(authors, list) and bool(authors)

    has_metadata_author = (
        isinstance(metadata, dict)
        and non_empty_string(metadata.get("author_name"))
    )

    if not has_task_authors and not has_metadata_author:
        errors.append(f"{task_dir}: missing author information")

    return errors


def validate_legacy_schema(
    task_dir: Path,
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if not non_empty_string(data.get("version")):
        errors.append(
            f"{task_dir}: legacy task must define a non-empty version"
        )

    metadata = data.get("metadata")

    if not isinstance(metadata, dict):
        errors.append(f"{task_dir}: legacy task missing [metadata] section")
        return errors

    if not non_empty_string(metadata.get("author_name")):
        errors.append(
            f"{task_dir}: metadata.author_name "
            "must be a non-empty string"
        )

    return errors


def validate_execution_config(
    task_dir: Path,
    data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    verifier = data.get("verifier")

    if not isinstance(verifier, dict):
        errors.append(f"{task_dir}: missing [verifier] section")
    elif not positive_number(verifier.get("timeout_sec")):
        errors.append(
            f"{task_dir}: verifier.timeout_sec "
            "must be a positive number"
        )

    agent = data.get("agent")

    if not isinstance(agent, dict):
        errors.append(f"{task_dir}: missing [agent] section")
    elif not positive_number(agent.get("timeout_sec")):
        errors.append(
            f"{task_dir}: agent.timeout_sec "
            "must be a positive number"
        )

    environment = data.get("environment")

    if isinstance(environment, dict):
        optional_positive_fields = (
            "build_timeout_sec",
            "cpus",
            "memory_mb",
            "storage_mb",
        )

        for field in optional_positive_fields:
            if field in environment and not positive_number(
                environment[field]
            ):
                errors.append(
                    f"{task_dir}: environment.{field} "
                    "must be a positive number"
                )

        if (
            "gpus" in environment
            and not non_negative_number(environment["gpus"])
        ):
            errors.append(
                f"{task_dir}: environment.gpus "
                "must be a non-negative number"
            )

    return errors


def validate_task_metadata(task_dir: Path) -> list[str]:
    try:
        data = load_task_metadata(task_dir)
    except tomllib.TOMLDecodeError as exc:
        return [f"{task_dir}: invalid TOML: {exc}"]

    errors: list[str] = []

    if "task" in data:
        errors.extend(validate_modern_schema(task_dir, data))
    else:
        errors.extend(validate_legacy_schema(task_dir, data))

    errors.extend(validate_execution_config(task_dir, data))

    return errors


def main() -> int:
    tasks = task_directories()

    if not tasks:
        logger.error("no_benchmark_tasks_discovered")
        return 1

    errors: list[str] = []

    for task_dir in tasks:
        errors.extend(validate_task_metadata(task_dir))

    if errors:
        logger.error(
            "task_metadata_validation_failed errors=%d",
            len(errors),
        )

        for error in errors:
            logger.error(
                "task_metadata_invalid detail=%s",
                error,
            )

        return 1

    logger.info(
        "task_metadata_validation_success tasks=%d",
        len(tasks),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
