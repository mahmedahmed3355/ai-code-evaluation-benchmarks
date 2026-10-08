#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
OUTPUT = ROOT / "build" / "resolved_config.txt"

PROTECTED = {
    "BUILD_TYPE",
    "OPT_LEVEL",
    "FAST_MATH",
    "VECTOR_WIDTH",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
}


def load_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    base = load_config(CONFIG_DIR / "build.conf")
    profile = load_config(CONFIG_DIR / "release.profile")
    benchmark = load_config(CONFIG_DIR / "benchmark.conf")
    local = load_config(CONFIG_DIR / "local.override")

    config = dict(base)
    config.update(profile)

    for key, value in local.items():
        if key not in PROTECTED:
            config[key] = value

    for key in benchmark:
        if key not in config:
            config[key] = benchmark[key]

    OUTPUT.write_text("".join(f"{key}={value}\n" for key, value in sorted(config.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
