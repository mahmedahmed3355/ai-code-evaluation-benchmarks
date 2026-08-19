#!/usr/bin/env python3

from pathlib import Path

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

    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    artifact = ARTIFACTS / "kernel_build.artifact"

    keys = [
        "ALLOCATOR",
        "MEMORY_POOL",
        "STREAM_ORDERED",
        "REUSE",
        "SYNC_MODE",
        "POOL_CHUNK_SIZE",
        "MAX_POOL_BLOCKS",
        "ALLOCATION_BATCH",
    ]

    with artifact.open("w") as out:
        for key in keys:
            if key in config:
                out.write(f"{key}={config[key]}\n")

        out.write(f"WORKLOAD_COUNT={plan['WORKLOAD_COUNT']}\n")

        for index in range(1, int(plan["WORKLOAD_COUNT"]) + 1):
            for key in [
                "NAME",
                "INPUT_SIZE",
                "ALLOCATIONS",
                "STREAMS",
                "WORK_UNITS",
            ]:
                out.write(f"WORKLOAD_{index}_{key}={plan[f'WORKLOAD_{index}_{key}']}\n")

        out.write(f"TOTAL_WORK_UNITS={plan['TOTAL_WORK_UNITS']}\n")

    print(f"Generated artifact: {artifact}")


if __name__ == "__main__":
    main()
