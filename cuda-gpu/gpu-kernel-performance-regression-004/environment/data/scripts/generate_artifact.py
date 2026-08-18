#!/usr/bin/env python3

import hashlib
import sys
from pathlib import Path

ROOT = Path("/app")
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"


def parse_key_values(path: Path) -> dict[str, str]:
    values = {}

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def file_digest(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def generate_artifact() -> Path:
    config_path = BUILD_DIR / "resolved_config.txt"
    plan_path = BUILD_DIR / "execution_plan.txt"

    if not config_path.exists():
        raise FileNotFoundError(config_path)

    if not plan_path.exists():
        raise FileNotFoundError(plan_path)

    config = parse_key_values(config_path)
    plan = parse_key_values(plan_path)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    artifact = ARTIFACT_DIR / "kernel_build.artifact"

    lines = [
        "GPU_KERNEL_BUILD_ARTIFACT",
        "FORMAT_VERSION=1",
        "",
        f"CONFIG_SHA256={file_digest(config_path)}",
        f"PLAN_SHA256={file_digest(plan_path)}",
        "",
        f"BUILD_TYPE={config.get('BUILD_TYPE', 'unknown')}",
        f"OPT_LEVEL={config.get('OPT_LEVEL', 'unknown')}",
        f"STRATEGY={config.get('STRATEGY', 'unknown')}",
        f"BLOCK_SIZE={config.get('BLOCK_SIZE', 'unknown')}",
        f"CHUNK_SIZE={config.get('CHUNK_SIZE', 'unknown')}",
        f"VECTOR_WIDTH={config.get('VECTOR_WIDTH', 'unknown')}",
        f"FAST_PATH={config.get('FAST_PATH', 'unknown')}",
        f"WORK_UNIT_COST={config.get('WORK_UNIT_COST', 'unknown')}",
        f"ARTIFACT_MODE={config.get('ARTIFACT_MODE', 'unknown')}",
        "",
        f"TOTAL_WORK_UNITS={plan.get('TOTAL_WORK_UNITS', 'unknown')}",
        "",
    ]

    workload_index = 1

    while True:
        input_key = (
            f"WORKLOAD_{workload_index}_INPUT_SIZE"
        )
        work_key = (
            f"WORKLOAD_{workload_index}_WORK_UNITS"
        )

        if input_key not in plan:
            break

        lines.append(
            f"{input_key}={plan[input_key]}"
        )
        lines.append(
            f"{work_key}={plan[work_key]}"
        )

        workload_index += 1

    artifact.write_text(
        "\n".join(lines) + "\n"
    )

    return artifact


def main() -> int:
    try:
        artifact = generate_artifact()
    except Exception as exc:
        print(
            f"ERROR: {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Generated artifact: {artifact}")
    print(
        f"Artifact SHA256: {file_digest(artifact)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
