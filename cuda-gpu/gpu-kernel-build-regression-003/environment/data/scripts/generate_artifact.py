#!/usr/bin/env python3
import hashlib
import sys
from pathlib import Path

CONTRACT_KEYS = (
    "BUILD_TYPE",
    "OPT_LEVEL",
    "FAST_MATH",
    "VECTOR_WIDTH",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
)


def parse_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    if len(sys.argv) != 3:
        return 2

    config_path = Path(sys.argv[1])
    artifact_path = Path(sys.argv[2])
    config = parse_config(config_path)

    missing = [key for key in CONTRACT_KEYS if key not in config]
    if missing:
        print("missing configuration values: " + ", ".join(missing), file=sys.stderr)
        return 1

    canonical = "".join(f"{key}={config[key]}\n" for key in CONTRACT_KEYS)
    digest = hashlib.sha256(canonical.encode()).hexdigest()

    artifact = (
        "GPU_KERNEL_BUILD_ARTIFACT\n"
        "FORMAT_VERSION=2\n"
        f"CONFIG_SHA256={digest}\n"
        + "".join(f"{key}={config[key]}\n" for key in CONTRACT_KEYS)
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
