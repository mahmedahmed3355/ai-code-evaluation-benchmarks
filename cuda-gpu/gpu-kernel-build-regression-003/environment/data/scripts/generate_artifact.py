#!/usr/bin/env python3

import hashlib
import sys
from pathlib import Path


def parse_config(path: Path) -> dict[str, str]:
    config: dict[str, str] = {}

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()

    return config


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: generate_artifact.py <effective_config> <artifact>",
            file=sys.stderr,
        )
        return 2

    config_path = Path(sys.argv[1])
    artifact_path = Path(sys.argv[2])

    config = parse_config(config_path)

    required = {
        "BUILD_TYPE",
        "OPT_LEVEL",
        "FAST_MATH",
        "VECTOR_WIDTH",
        "DEBUG_SYMBOLS",
        "LTO",
    }

    missing = sorted(required - config.keys())

    if missing:
        print(
            f"missing configuration values: {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    canonical = "\n".join(
        f"{key}={config[key]}"
        for key in sorted(config)
    ) + "\n"

    digest = hashlib.sha256(canonical.encode()).hexdigest()

    artifact = (
        "GPU_KERNEL_BUILD_ARTIFACT\n"
        "FORMAT_VERSION=1\n"
        f"CONFIG_SHA256={digest}\n"
        f"BUILD_TYPE={config['BUILD_TYPE']}\n"
        f"OPT_LEVEL={config['OPT_LEVEL']}\n"
        f"FAST_MATH={config['FAST_MATH']}\n"
        f"VECTOR_WIDTH={config['VECTOR_WIDTH']}\n"
        f"DEBUG_SYMBOLS={config['DEBUG_SYMBOLS']}\n"
        f"LTO={config['LTO']}\n"
        f"ARTIFACT_MODE={config.get('ARTIFACT_MODE', 'optimized')}\n"
    )

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(artifact)

    print(f"Generated artifact: {artifact_path}")
    print(f"Configuration digest: {digest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
