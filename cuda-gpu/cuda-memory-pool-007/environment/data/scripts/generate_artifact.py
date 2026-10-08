#!/usr/bin/env python3
from pathlib import Path
import hashlib

BUILD = Path("/app/build")
ARTIFACTS = Path("/app/artifacts")

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
    config = parse(BUILD / "resolved_config.txt")
    plan = parse(BUILD / "execution_plan.txt")
    provenance = parse(BUILD / "config_provenance.txt")
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    artifact = ARTIFACTS / "kernel_build.artifact"
    keys = [
        "ALLOCATOR","MEMORY_POOL","STREAM_ORDERED","REUSE","SYNC_MODE",
        "POOL_CHUNK_SIZE","MAX_POOL_BLOCKS","ALLOCATION_BATCH",
    ]
    with artifact.open("w") as out:
        for key in keys:
            out.write(f"{key}={config[key]}\n")
        out.write(f"WORKLOAD_COUNT={plan['WORKLOAD_COUNT']}\n")
        for index in range(1, int(plan["WORKLOAD_COUNT"]) + 1):
            for key in ["NAME","INPUT_SIZE","ALLOCATIONS","STREAMS","REUSE_RATIO","WORK_UNITS"]:
                out.write(f"WORKLOAD_{index}_{key}={plan[f'WORKLOAD_{index}_{key}']}\n")
        out.write(f"TOTAL_WORK_UNITS={plan['TOTAL_WORK_UNITS']}\n")
        out.write("CONFIG_PROVENANCE=recorded\n")
    material = (
        (BUILD / "resolved_config.txt").read_text()
        + (BUILD / "config_provenance.txt").read_text()
        + (BUILD / "execution_plan.txt").read_text()
    ).encode()
    digest = hashlib.sha256(material).hexdigest()
    (ARTIFACTS / "kernel_build.provenance").write_text(
        f"RESOLVED_CONFIG_SHA256={hashlib.sha256((BUILD/'resolved_config.txt').read_bytes()).hexdigest()}\n"
        f"PLAN_SHA256={hashlib.sha256((BUILD/'execution_plan.txt').read_bytes()).hexdigest()}\n"
        f"CONFIG_AND_PLAN_SHA256={digest}\n"
        f"ALLOCATOR_SOURCE={provenance['ALLOCATOR']}\n"
        f"MEMORY_POOL_SOURCE={provenance['MEMORY_POOL']}\n"
        f"STREAM_ORDERED_SOURCE={provenance['STREAM_ORDERED']}\n"
        f"REUSE_SOURCE={provenance['REUSE']}\n"
        f"SYNC_MODE_SOURCE={provenance['SYNC_MODE']}\n"
    )
    print(f"Generated artifact: {artifact}")

if __name__ == "__main__":
    main()
