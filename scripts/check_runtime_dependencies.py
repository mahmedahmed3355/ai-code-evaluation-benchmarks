from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.logging_config import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"


def get_runtime_dependencies() -> list[str]:
    with PYPROJECT.open("rb") as file:
        data = tomllib.load(file)

    dependencies = data.get("project", {}).get("dependencies", [])

    if not isinstance(dependencies, list):
        raise ValueError("project.dependencies must be a list")

    return [str(dependency) for dependency in dependencies]


def validate_runtime_dependencies() -> list[str]:
    dependencies = get_runtime_dependencies()

    if not dependencies:
        raise ValueError(
            "Repository runtime dependency set is empty. "
            "Declare repository-level runtime dependencies explicitly."
        )

    logger.info(
        "runtime_dependencies_validated count=%d dependencies=%s",
        len(dependencies),
        dependencies,
    )

    return dependencies


def main() -> int:
    validate_runtime_dependencies()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
