from __future__ import annotations

import re
from pathlib import Path

from scripts.logging_config import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]

PIP_INSTALL_RE = re.compile(
    r"\bpip(?:3)?\s+install\b(.*)",
    re.IGNORECASE,
)

CONTINUATION_RE = re.compile(r"\\\s*$")


def dockerfiles() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("Dockerfile")
        if ".git" not in path.parts and ".venv" not in path.parts
    )


def docker_instructions(text: str) -> list[str]:
    instructions: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        current.append(line)

        if CONTINUATION_RE.search(line):
            continue

        instructions.append("\n".join(current))
        current = []

    if current:
        instructions.append("\n".join(current))

    return instructions


def pip_dependencies(instruction: str) -> list[str]:
    normalized = instruction.replace("\\\n", " ")

    match = PIP_INSTALL_RE.search(normalized)
    if not match:
        return []

    dependencies: list[str] = []
    tokens = match.group(1).split()

    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token in {"&&", ";", "\\"}:
            break

        if token in {"-r", "--requirement", "-c", "--constraint"}:
            index += 2
            continue

        if (
            token.startswith("-r")
            or token.startswith("--requirement=")
            or token.startswith("-c")
            or token.startswith("--constraint=")
        ):
            index += 1
            continue

        if token.startswith("-"):
            index += 1
            continue

        if token == ".":
            index += 1
            continue

        dependencies.append(token)
        index += 1

    return dependencies


def check_file(path: Path) -> list[str]:
    errors: list[str] = []

    text = path.read_text(encoding="utf-8", errors="ignore")

    for instruction in docker_instructions(text):
        dependencies = pip_dependencies(instruction)

        for dependency in dependencies:
            if (
                "==" not in dependency
                and "@git+" not in dependency
                and "@http" not in dependency
            ):
                errors.append(
                    f"{path.relative_to(ROOT)}: unpinned pip dependency "
                    f"{dependency}"
                )

    return errors


def main() -> int:
    files = dockerfiles()
    failures: list[str] = []

    for dockerfile in files:
        failures.extend(check_file(dockerfile))

    print(f"Scanned Dockerfiles: {len(files)}")

    if failures:
        print("\nDependency issues:")
        for failure in failures:
            print(f"  - {failure}")

        logger.error(
            "task_dependency_validation_failed files=%d issues=%d",
            len(files),
            len(failures),
        )
        return 1

    logger.info(
        "task_dependency_validation_success files=%d issues=0",
        len(files),
    )

    print("All task dependency manifests and Dockerfile installs are pinned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
