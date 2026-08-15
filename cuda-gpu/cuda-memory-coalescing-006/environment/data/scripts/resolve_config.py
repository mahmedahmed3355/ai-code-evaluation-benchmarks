#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
OUT = ROOT / "build" / "resolved_config.txt"

FILES = [
    CONFIG_DIR / "build.conf",
    CONFIG_DIR / "release.profile",
    CONFIG_DIR / "benchmark.conf",
    CONFIG_DIR / "local.override",
]


def parse(path):
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

    for path in FILES:
        values = parse(path)
        resolved.update(values)

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={resolved[key]}\n")

    print(f"Resolved configuration written to {OUT}")

    for key in sorted(resolved):
        print(f"{key}={resolved[key]}")


if __name__ == "__main__":
    main()
