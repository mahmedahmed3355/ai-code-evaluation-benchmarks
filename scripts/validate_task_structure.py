from __future__ import annotations

from pathlib import Path

from scripts.logging_config import get_logger

ROOT = Path(__file__).resolve().parents[1]
logger = get_logger(__name__)

REQUIRED_ANY_OF = (
    ("instruction.md", "instruction_en.md"),
)

REQUIRED_PATHS = (
    "task.toml",
    "environment",
    "solution/solve.sh",
    "tests",
    "tests/Dockerfile",
    "tests/test.sh",
)


def task_directories(root: Path) -> list[Path]:
    task_dirs = [path.parent for path in root.rglob("task.toml")]

    return sorted(
        task_dirs,
        key=lambda path: (
            len(path.relative_to(root).parts),
            str(path.relative_to(root)),
        ),
    )


def validate_task(task_dir: Path) -> list[str]:
    """Return validation errors for one benchmark task."""
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        path = task_dir / relative_path

        if not path.exists():
            errors.append(f"missing required path: {relative_path}")

    for alternatives in REQUIRED_ANY_OF:
        if not any((task_dir / path).is_file() for path in alternatives):
            joined = " or ".join(alternatives)
            errors.append(f"missing instruction file: {joined}")

    environment_dir = task_dir / "environment"

    if environment_dir.is_dir():
        dockerfile = environment_dir / "Dockerfile"
        compose_file = environment_dir / "docker-compose.yaml"
        compose_yml = environment_dir / "docker-compose.yml"

        if not (
            dockerfile.is_file()
            or compose_file.is_file()
            or compose_yml.is_file()
        ):
            errors.append(
                "environment must contain Dockerfile or docker-compose file"
            )

    solution = task_dir / "solution" / "solve.sh"

    if solution.is_file() and solution.stat().st_size == 0:
        errors.append("solution/solve.sh must not be empty")

    test_script = task_dir / "tests" / "test.sh"

    if test_script.is_file() and test_script.stat().st_size == 0:
        errors.append("tests/test.sh must not be empty")

    return errors


def main() -> int:
    tasks = task_directories(ROOT)

    logger.info("benchmark_tasks_discovered count=%d", len(tasks))

    failures: list[tuple[Path, list[str]]] = []

    for task_dir in tasks:
        errors = validate_task(task_dir)

        if errors:
            failures.append((task_dir, errors))

    if failures:
        logger.error(
            "task_structure_validation_failed failures=%d",
            len(failures),
        )

        for task_dir, errors in failures:
            relative = task_dir.relative_to(ROOT)

            logger.error(
                "task_structure_invalid task=%s errors=%s",
                relative,
                "; ".join(errors),
            )

        return 1

    logger.info(
        "task_structure_validation_success tasks=%d",
        len(tasks),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
