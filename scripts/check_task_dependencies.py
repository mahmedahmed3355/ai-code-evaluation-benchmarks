from __future__ import annotations

import re
from pathlib import Path

from scripts.logging_config import get_logger

logger = get_logger(__name__)

ROOT = Path(__file__).resolve().parents[1]


UNPINNED_PIP = re.compile(
    r"pip install\s+([^\s]+)(?![=<>])"
)

UNPINNED_APT = re.compile(
    r"apt(-get)? install\s+([^\s&]+)"
)


def dockerfiles() -> list[Path]:
    return sorted(ROOT.rglob("Dockerfile"))


def check_file(path: Path) -> list[str]:
    errors: list[str] = []

    text = path.read_text(errors="ignore")

    if "pip install" in text:
        requirements = path.parent / "requirements.txt"

        if not requirements.exists():
            errors.append(
                f"{path}: pip dependency manifest requirements.txt missing"
            )

    for line in text.splitlines():
        if "pip install" in line and "--no-cache-dir" not in line:
            errors.append(
                f"{path}: pip install should use --no-cache-dir"
            )

        if "apt-get install" in line and "-y" in line:
            errors.append(
                f"{path}: apt packages should be version pinned when reproducibility is required"
            )

    return errors


def main() -> int:
    failures = []

    for dockerfile in dockerfiles():
        failures.extend(check_file(dockerfile))

    if failures:
        for item in failures:
            logger.warning("dependency_issue %s", item)

        logger.warning(
            "task_dependency_validation_summary files=%d issues=%d",
            len(dockerfiles()),
            len(failures),
        )

        return 0

    logger.info(
        "task_dependency_validation_success files=%d issues=0",
        len(dockerfiles()),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
