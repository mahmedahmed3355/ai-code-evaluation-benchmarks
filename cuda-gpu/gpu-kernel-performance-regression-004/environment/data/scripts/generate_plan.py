#!/usr/bin/env python3

import math
import sys
from pathlib import Path

ROOT = Path("/app")
BUILD_DIR = ROOT / "build"
DATASET = ROOT / "datasets" / "workload.csv"

def parse(path):
    values = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values

def workload_rows():
    rows = []
    lines = DATASET.read_text().splitlines()
    if not lines:
        raise ValueError("empty workload dataset")
    header = lines[0].split(",")
    positions = {name: header.index(name) for name in ["workload_id", "input_size", "expected_output", "profile", "budget_key"]}
    for raw in lines[1:]:
        if not raw.strip():
            continue
        fields = raw.split(",")
        if len(fields) != len(header):
            raise ValueError("malformed workload row")
        rows.append({name: fields[index].strip() for name, index in positions.items()})
    return rows

def calculate_work(size, block, chunk, strategy, vector, fast, cost):
    chunks = math.ceil(size / chunk)
    if strategy == "blocked":
        base = chunks
    elif strategy == "tiled":
        base = chunks * 2
    elif strategy == "scalar":
        base = math.ceil(size / block) * chunks
    else:
        raise ValueError(f"unsupported strategy: {strategy}")
    return base * max(1, 4 // vector) * (1 if fast else 2) * cost

def main():
    config_path = BUILD_DIR / "resolved_config.txt"
    if not config_path.exists():
        print("ERROR: resolved configuration is missing.", file=sys.stderr)
        return 1
    config = parse(config_path)
    block = int(config["BLOCK_SIZE"])
    chunk = int(config["CHUNK_SIZE"])
    vector = int(config["VECTOR_WIDTH"])
    fast = int(config["FAST_PATH"])
    cost = int(config["WORK_UNIT_COST"])
    strategy = config["STRATEGY"]
    lines = [
        "GPU_EXECUTION_PLAN",
        f"PROFILE={config['PROFILE']}",
        f"STRATEGY={strategy}",
        f"BLOCK_SIZE={block}",
        f"CHUNK_SIZE={chunk}",
        f"VECTOR_WIDTH={vector}",
        f"FAST_PATH={fast}",
        f"WORK_UNIT_COST={cost}",
    ]
    total = 0
    for index, row in enumerate(workload_rows(), 1):
        work = calculate_work(int(row["input_size"]), block, chunk, strategy, vector, fast, cost)
        total += work
        lines.extend([
            f"WORKLOAD_{index}_ID={row['workload_id']}",
            f"WORKLOAD_{index}_INPUT_SIZE={row['input_size']}",
            f"WORKLOAD_{index}_PROFILE={row['profile']}",
            f"WORKLOAD_{index}_BUDGET_KEY={row['budget_key']}",
            f"WORKLOAD_{index}_WORK_UNITS={work}",
        ])
    lines.append(f"TOTAL_WORK_UNITS={total}")
    output = BUILD_DIR / "execution_plan.txt"
    output.write_text("\n".join(lines) + "\n")
    print(f"Execution plan written to {output}")
    print(f"Total work units: {total}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
