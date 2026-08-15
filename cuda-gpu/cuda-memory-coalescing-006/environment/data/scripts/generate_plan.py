#!/usr/bin/env python3

from pathlib import Path
import csv

ROOT = Path("/app")
CONFIG = ROOT / "build" / "resolved_config.txt"
DATASET = ROOT / "datasets" / "workload.csv"
PLAN = ROOT / "build" / "execution_plan.txt"


def parse_config():
    values = {}

    for line in CONFIG.read_text().splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def work_units(input_size, cfg):
    block = int(cfg["BLOCK_SIZE"])
    vector_width = int(cfg["VECTOR_WIDTH"])
    coalesced = int(cfg["COALESCED_ACCESS"])
    aligned = int(cfg["ALIGNED_ACCESS"])
    fast_path = int(cfg["FAST_PATH"])

    base = (input_size + block - 1) // block

    # Poor memory access causes excessive work.
    penalty = 1

    if coalesced == 0:
        penalty *= 8

    if aligned == 0:
        penalty *= 4

    if vector_width == 1:
        penalty *= 2

    if fast_path == 0:
        penalty *= 2

    # Optimized/vectorized path reduces memory transactions.
    return base * penalty


def main():
    cfg = parse_config()

    rows = []
    total = 0

    with DATASET.open() as f:
        for row in csv.DictReader(f):
            size = int(row["input_size"])
            units = work_units(size, cfg)

            rows.append((row["name"], size, units))
            total += units

    PLAN.parent.mkdir(parents=True, exist_ok=True)

    with PLAN.open("w") as f:
        f.write(f"TOTAL_WORK_UNITS={total}\n")

        for index, (_, size, units) in enumerate(rows, 1):
            f.write(f"WORKLOAD_{index}_INPUT_SIZE={size}\n")
            f.write(f"WORKLOAD_{index}_WORK_UNITS={units}\n")

    print(f"Execution plan written to {PLAN}")
    print(f"Total work units: {total}")

    for name, size, units in rows:
        print(f"{name}: input={size} work_units={units}")


if __name__ == "__main__":
    main()
