from __future__ import annotations

import tomllib
from pathlib import Path

from scripts.logging_config import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]

OUTPUT = ROOT / "docs" / "TASK_DEPENDENCIES.md"


def find_requirements(task: Path) -> list[str]:
    requirements: list[str] = []

    for req in task.rglob("requirements.txt"):
        for line in req.read_text().splitlines():
            line = line.strip()

            if line and not line.startswith("#"):
                requirements.append(line)

    return sorted(set(requirements))




def find_repository_dependencies() -> tuple[list[str], list[str]]:
    pyproject = ROOT / "pyproject.toml"

    if not pyproject.exists():
        return [], []

    with pyproject.open("rb") as f:
        data = tomllib.load(f)

    runtime = data.get("project", {}).get("dependencies", [])

    dev = (
        data.get("dependency-groups", {})
        .get("dev", [])
    )

    return sorted(runtime), sorted(dev)


def generate() -> Path:
    lines = [
        "# Task Dependency Inventory",
        "",
        "Generated dependency inventory for benchmark task environments.",
        "",
    ]

    runtime_deps, dev_deps = find_repository_dependencies()

    if runtime_deps:
        lines.extend([
            "## Repository Runtime Dependencies",
            "",
        ])

        for dep in runtime_deps:
            lines.append(f"- `{dep}`")

        lines.append("")

    if dev_deps:
        lines.extend([
            "## Repository Development Dependencies",
            "",
        ])

        for dep in dev_deps:
            lines.append(f"- `{dep}`")

        lines.append("")

    found = False

    for task_file in sorted(ROOT.rglob("task.toml")):
        task = task_file.parent
        deps = find_requirements(task)

        if not deps:
            continue

        found = True

        lines.extend(
            [
                f"## {task.relative_to(ROOT)}",
                "",
            ]
        )

        for dep in deps:
            lines.append(f"- `{dep}`")

        lines.append("")

    if not found:
        lines.extend(
            [
                "No task-local requirements manifests found.",
                "",
            ]
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines))

    logger.info(
        "dependency_inventory_generated file=%s",
        OUTPUT,
    )

    return OUTPUT


def main() -> int:
    generate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
