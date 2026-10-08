#!/usr/bin/env python3

import hashlib
from pathlib import Path

ROOT = Path("/app")
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"

def parse(path):
    values = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    config_path = BUILD_DIR / "resolved_config.txt"
    plan_path = BUILD_DIR / "execution_plan.txt"
    if not config_path.exists() or not plan_path.exists():
        raise SystemExit("build inputs are incomplete")
    config = parse(config_path)
    plan = parse(plan_path)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "GPU_KERNEL_BUILD_ARTIFACT",
        "FORMAT_VERSION=2",
        f"CONFIG_SHA256={digest(config_path)}",
        f"PLAN_SHA256={digest(plan_path)}",
        f"PROFILE={config['PROFILE']}",
        f"BUILD_TYPE={config['BUILD_TYPE']}",
        f"OPT_LEVEL={config['OPT_LEVEL']}",
        f"STRATEGY={config['STRATEGY']}",
        f"BLOCK_SIZE={config['BLOCK_SIZE']}",
        f"CHUNK_SIZE={config['CHUNK_SIZE']}",
        f"VECTOR_WIDTH={config['VECTOR_WIDTH']}",
        f"FAST_PATH={config['FAST_PATH']}",
        f"WORK_UNIT_COST={config['WORK_UNIT_COST']}",
        f"ARTIFACT_MODE={config['ARTIFACT_MODE']}",
        f"TOTAL_WORK_UNITS={plan['TOTAL_WORK_UNITS']}",
    ]
    for index in range(1, 100):
        key = f"WORKLOAD_{index}_ID"
        if key not in plan:
            break
        for suffix in ["ID", "INPUT_SIZE", "PROFILE", "BUDGET_KEY", "WORK_UNITS"]:
            k = f"WORKLOAD_{index}_{suffix}"
            lines.append(f"{k}={plan[k]}")
    artifact = ARTIFACT_DIR / "kernel_build.artifact"
    artifact.write_text("\n".join(lines) + "\n")
    print(f"Generated artifact: {artifact}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
