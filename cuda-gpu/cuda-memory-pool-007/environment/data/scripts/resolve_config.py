#!/usr/bin/env python3

from pathlib import Path

CONFIG_DIR = Path("/app/configs")
BUILD_DIR = Path("/app/build")

SOURCES = [
    CONFIG_DIR / "build.conf",
    CONFIG_DIR / "release.profile",
    CONFIG_DIR / "benchmark.conf",
    CONFIG_DIR / "local.override",
]


def parse_config(path):
    values = {}

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def main():
    resolved = {}

    for source in SOURCES:
        if not source.exists():
            continue

        resolved.update(parse_config(source))

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    output = BUILD_DIR / "resolved_config.txt"

    with output.open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={resolved[key]}\n")

    print(f"Resolved configuration written to {output}")

    for key in sorted(resolved):
        print(f"{key}={resolved[key]}")


if __name__ == "__main__":
    main()
