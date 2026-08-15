#!/usr/bin/env python3

from pathlib import Path
import hashlib
import sys


ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"


SOURCES = [
    "build.conf",
    "release.profile",
    "benchmark.conf",
    "local.override",
]


def parse_config(path: Path) -> dict[str, str]:
    values = {}

    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)

        values[key.strip()] = value.strip()

    return values


def load_all_configs() -> list[tuple[str, dict[str, str]]]:
    configs = []

    for name in SOURCES:
        path = CONFIG_DIR / name

        if path.exists():
            configs.append(
                (name, parse_config(path))
            )

    return configs


def resolve() -> dict[str, str]:
    resolved = {}

    for _, values in load_all_configs():
        resolved.update(values)

    return resolved


def write_resolved(values: dict[str, str]) -> Path:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    output = BUILD_DIR / "resolved_config.txt"

    lines = [
        f"{key}={values[key]}"
        for key in sorted(values)
    ]

    output.write_text("\n".join(lines) + "\n")

    return output


def digest(values: dict[str, str]) -> str:
    payload = "\n".join(
        f"{key}={values[key]}"
        for key in sorted(values)
    )

    return hashlib.sha256(
        payload.encode()
    ).hexdigest()


def main() -> int:
    values = resolve()
    output = write_resolved(values)

    print(
        f"Resolved configuration written to {output}"
    )

    print(
        f"Configuration digest: {digest(values)}"
    )

    for key in sorted(values):
        print(f"{key}={values[key]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
