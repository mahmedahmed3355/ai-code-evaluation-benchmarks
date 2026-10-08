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
    provenance = {}
    for source in SOURCES:
        if not source.exists():
            continue
        for key, value in parse_config(source).items():
            resolved[key] = value
            provenance[key] = source.name

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    with (BUILD_DIR / "resolved_config.txt").open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={resolved[key]}\n")
    with (BUILD_DIR / "config_provenance.txt").open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={provenance[key]}\n")

    print(f"Resolved configuration written to {BUILD_DIR / 'resolved_config.txt'}")
    print(f"Configuration provenance written to {BUILD_DIR / 'config_provenance.txt'}")

if __name__ == "__main__":
    main()
