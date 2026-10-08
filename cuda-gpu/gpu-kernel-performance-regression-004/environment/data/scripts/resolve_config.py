#!/usr/bin/env python3

import hashlib
from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"

SOURCES = ["build.conf", "release.profile", "benchmark.conf", "local.override"]

PROTECTED_KEYS = {
    "PROFILE",
    "OPT_PROFILE",
    "OPT_LEVEL",
    "STRATEGY",
    "BLOCK_SIZE",
    "CHUNK_SIZE",
    "VECTOR_WIDTH",
    "FAST_PATH",
    "WORK_UNIT_COST",
    "MAX_WORK_UNITS",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
}

def parse_config(path):
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

def load_all_configs():
    return [(name, parse_config(CONFIG_DIR / name)) for name in SOURCES]

def resolve():
    configs = dict(load_all_configs())
    resolved = {}
    resolved.update(configs["build.conf"])
    resolved.update(configs["release.profile"])
    resolved.update(configs["benchmark.conf"])
    resolved.update(configs["local.override"])
    return resolved

def digest(values):
    payload = "\n".join(f"{key}={values[key]}" for key in sorted(values))
    return hashlib.sha256(payload.encode()).hexdigest()

def main():
    values = resolve()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    output = BUILD_DIR / "resolved_config.txt"
    output.write_text("\n".join(f"{key}={values[key]}" for key in sorted(values)) + "\n")
    print(f"Resolved configuration written to {output}")
    print(f"Configuration digest: {digest(values)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
