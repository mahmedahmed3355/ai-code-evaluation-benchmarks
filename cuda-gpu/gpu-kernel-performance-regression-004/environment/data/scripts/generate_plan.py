#!/usr/bin/env python3

import math
import sys
from pathlib import Path

ROOT = Path("/app")
BUILD_DIR = ROOT / "build"
DATASET = ROOT / "datasets" / "workload.csv"


def parse_config(path: Path) -> dict[str, str]:
    values = {}

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def parse_int(config: dict[str, str], key: str) -> int:
    return int(config[key])


def strategy_factor(strategy: str) -> int:
    factors = {
        "blocked": 1,
        "tiled": 2,
        "scalar": 8,
    }

    if strategy not in factors:
        raise ValueError(f"Unsupported strategy: {strategy}")

    return factors[strategy]


def vector_factor(width: int) -> int:
    if width <= 0:
        raise ValueError("VECTOR_WIDTH must be positive")

    return max(1, 4 // width)


def workload_sizes() -> list[int]:
    sizes = []

    if not DATASET.exists():
        raise FileNotFoundError(DATASET)

    lines = DATASET.read_text().splitlines()

    for line in lines[1:]:
        if not line.strip():
            continue

        fields = line.split(",")

        if len(fields) < 2:
            raise ValueError("Malformed workload row")

        sizes.append(int(fields[1]))

    if not sizes:
        raise ValueError("No workloads found")

    return sizes


def calculate_work(
    input_size: int,
    block_size: int,
    chunk_size: int,
    strategy: str,
    vector_width: int,
    fast_path: int,
    work_unit_cost: int,
) -> int:
    chunks = math.ceil(input_size / chunk_size)

    if strategy == "blocked":
        strategy_work = chunks
    elif strategy == "tiled":
        strategy_work = chunks * 2
    elif strategy == "scalar":
        blocks = math.ceil(input_size / block_size)
        strategy_work = blocks * chunks
    else:
        raise ValueError(f"Unsupported strategy: {strategy}")

    vector_multiplier = max(1, 4 // vector_width)
    fast_multiplier = 1 if fast_path else 2

    return (
        strategy_work
        * vector_multiplier
        * fast_multiplier
        * work_unit_cost
    )


def build_plan(config: dict[str, str]) -> dict:
    strategy = config["STRATEGY"]
    block_size = parse_int(config, "BLOCK_SIZE")
    chunk_size = parse_int(config, "CHUNK_SIZE")
    vector_width = parse_int(config, "VECTOR_WIDTH")
    fast_path = parse_int(config, "FAST_PATH")
    work_unit_cost = parse_int(config, "WORK_UNIT_COST")

    workloads = workload_sizes()

    entries = []

    total_work = 0

    for size in workloads:
        work = calculate_work(
            input_size=size,
            block_size=block_size,
            chunk_size=chunk_size,
            strategy=strategy,
            vector_width=vector_width,
            fast_path=fast_path,
            work_unit_cost=work_unit_cost,
        )

        entries.append(
            {
                "input_size": size,
                "work_units": work,
            }
        )

        total_work += work

    return {
        "strategy": strategy,
        "block_size": block_size,
        "chunk_size": chunk_size,
        "vector_width": vector_width,
        "fast_path": fast_path,
        "work_unit_cost": work_unit_cost,
        "workloads": entries,
        "total_work_units": total_work,
    }


def write_plan(plan: dict) -> Path:
    output = BUILD_DIR / "execution_plan.txt"

    lines = [
        "GPU_EXECUTION_PLAN",
        f"STRATEGY={plan['strategy']}",
        f"BLOCK_SIZE={plan['block_size']}",
        f"CHUNK_SIZE={plan['chunk_size']}",
        f"VECTOR_WIDTH={plan['vector_width']}",
        f"FAST_PATH={plan['fast_path']}",
        f"WORK_UNIT_COST={plan['work_unit_cost']}",
        f"TOTAL_WORK_UNITS={plan['total_work_units']}",
    ]

    for index, workload in enumerate(plan["workloads"], start=1):
        lines.append(
            f"WORKLOAD_{index}_INPUT_SIZE="
            f"{workload['input_size']}"
        )
        lines.append(
            f"WORKLOAD_{index}_WORK_UNITS="
            f"{workload['work_units']}"
        )

    output.write_text("\n".join(lines) + "\n")

    return output


def main() -> int:
    config_path = BUILD_DIR / "resolved_config.txt"

    if not config_path.exists():
        print(
            "ERROR: resolved configuration is missing.",
            file=sys.stderr,
        )
        return 1

    config = parse_config(config_path)
    plan = build_plan(config)
    output = write_plan(plan)

    print(f"Execution plan written to {output}")
    print(f"Total work units: {plan['total_work_units']}")

    for workload in plan["workloads"]:
        print(
            f"input={workload['input_size']} "
            f"work_units={workload['work_units']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
