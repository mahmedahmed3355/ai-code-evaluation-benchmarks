from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "task.toml",
    "environment/Dockerfile",
    "tests/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
    "tests/test_outputs.py",
)


@dataclass(frozen=True)
class ImageBuildResult:
    attempted: bool
    succeeded: bool | None


@dataclass(frozen=True)
class TaskIsolationResult:
    task: Path
    missing: tuple[str, ...]
    environment: ImageBuildResult
    tests: ImageBuildResult

    @property
    def structurally_valid(self) -> bool:
        return not self.missing

    @property
    def passed(self) -> bool:
        if self.missing:
            return False

        for result in (self.environment, self.tests):
            if result.attempted and result.succeeded is not True:
                return False

        return True


def task_dirs(root: Path = ROOT) -> list[Path]:
    return sorted(path.parent for path in root.glob("*/*/task.toml"))


def missing_assets(task: Path) -> tuple[str, ...]:
    return tuple(relative for relative in REQUIRED_FILES if not (task / relative).is_file())


def docker_build(dockerfile: Path, context: Path, tag: str) -> bool:
    result = subprocess.run(
        [
            "docker",
            "build",
            "--pull=false",
            "--tag",
            tag,
            "--file",
            str(dockerfile),
            str(context),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def image_tag(task: Path, kind: str) -> str:
    try:
        name = "-".join(task.relative_to(ROOT).parts).lower()
    except ValueError:
        path_hash = hashlib.sha256(str(task.resolve()).encode()).hexdigest()[:12]
        name = f"{task.name}-{path_hash}"

    safe_name = "".join(
        character if character.isalnum() or character in "-_"
        else "-"
        for character in name
    )
    return f"benchmark-smoke-{safe_name}-{kind}"


def check_task(task: Path, *, build_images: bool = False) -> TaskIsolationResult:
    missing = missing_assets(task)
    not_attempted = ImageBuildResult(attempted=False, succeeded=None)

    if missing:
        return TaskIsolationResult(
            task=task,
            missing=missing,
            environment=not_attempted,
            tests=not_attempted,
        )

    if not build_images:
        return TaskIsolationResult(
            task=task,
            missing=(),
            environment=not_attempted,
            tests=not_attempted,
        )

    environment_ok = docker_build(
        task / "environment" / "Dockerfile",
        task,
        image_tag(task, "environment"),
    )

    tests_ok = docker_build(
        task / "tests" / "Dockerfile",
        task,
        image_tag(task, "tests"),
    )

    return TaskIsolationResult(
        task=task,
        missing=(),
        environment=ImageBuildResult(
            attempted=True,
            succeeded=environment_ok,
        ),
        tests=ImageBuildResult(
            attempted=True,
            succeeded=tests_ok,
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate benchmark task isolation and optionally build task images."
    )
    parser.add_argument(
        "--build-images",
        action="store_true",
        help="Build environment and verifier images after structural validation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tasks = task_dirs()

    if not tasks:
        print("ERROR: No benchmark tasks found.")
        return 1

    failures = 0

    if args.build_images:
        print(f"Checking isolation and building images for {len(tasks)} tasks\n")
    else:
        print(f"Checking structural isolation for {len(tasks)} tasks\n")

    for task in tasks:
        result = check_task(task, build_images=args.build_images)
        relative = task.relative_to(ROOT)

        if result.passed:
            print(f"PASS: {relative}")
            continue

        failures += 1
        print(f"FAIL: {relative}")

        for item in result.missing:
            print(f"  missing: {item}")

        if not result.missing:
            if result.environment.attempted and result.environment.succeeded is False:
                print("  environment image build failed")

            if result.tests.attempted and result.tests.succeeded is False:
                print("  tests image build failed")

    if failures:
        print(f"\nFAILED: {failures} task(s) did not satisfy isolation checks.")
        return 1

    if args.build_images:
        print(f"\nSUCCESS: All {len(tasks)} tasks passed isolation and image build checks.")
    else:
        print(f"\nSUCCESS: All {len(tasks)} tasks passed structural isolation checks.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
