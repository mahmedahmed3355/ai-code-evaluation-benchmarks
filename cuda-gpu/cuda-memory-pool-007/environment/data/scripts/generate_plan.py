#!/usr/bin/env python3
import csv, math
from pathlib import Path

CONFIG = Path("/app/build/resolved_config.txt")
DATASET = Path("/app/datasets/memory_pool.csv")
BUILD_DIR = Path("/app/build")

def parse_config(path):
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values

def enabled(values, key):
    return values.get(key, "0") == "1"

def workload_cost(row, values):
    input_size = int(row["input_size"])
    allocations = int(row["allocations"])
    streams = int(row["streams"])
    reuse_ratio = float(row["reuse_ratio"])
    chunk = int(values.get("POOL_CHUNK_SIZE", "1024"))

    cost = math.ceil(input_size / chunk) * 16
    if values.get("ALLOCATOR") == "legacy":
        cost += allocations * 8
        cost += streams * allocations
    if not enabled(values, "MEMORY_POOL"):
        cost += allocations * 4
    if not enabled(values, "STREAM_ORDERED"):
        cost += streams * allocations * 2
    if values.get("SYNC_MODE") == "global":
        cost += allocations * 3
    if not enabled(values, "REUSE"):
        cost += int(allocations * reuse_ratio * 6)
    if chunk < 4096:
        cost += allocations * (4096 // chunk)
    return cost

def main():
    values = parse_config(CONFIG)
    rows = list(csv.DictReader(DATASET.open(newline="")))
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    with (BUILD_DIR / "execution_plan.txt").open("w") as out:
        out.write(f"WORKLOAD_COUNT={len(rows)}\n")
        for index, row in enumerate(rows, 1):
            work = workload_cost(row, values)
            total += work
            out.write(
                f"WORKLOAD_{index}_NAME={row['workload']}\n"
                f"WORKLOAD_{index}_INPUT_SIZE={row['input_size']}\n"
                f"WORKLOAD_{index}_ALLOCATIONS={row['allocations']}\n"
                f"WORKLOAD_{index}_STREAMS={row['streams']}\n"
                f"WORKLOAD_{index}_REUSE_RATIO={row['reuse_ratio']}\n"
                f"WORKLOAD_{index}_WORK_UNITS={work}\n"
            )
        out.write(f"TOTAL_WORK_UNITS={total}\n")
    print(f"Execution plan written to {BUILD_DIR / 'execution_plan.txt'}")
    print(f"Total work units: {total}")

if __name__ == "__main__":
    main()
