#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
    "tests/test_outputs.py",
]

OPTIONAL_FILES = [
    "README.md",
    "tests/Dockerfile",
]

task_files = sorted(
    ROOT.glob("*/*/task.toml")
)

if not task_files:
    print("ERROR: No tasks found.")
    sys.exit(1)

failed = []

print(f"Found {len(task_files)} tasks\n")

for task_toml in task_files:
    task_dir = task_toml.parent
    missing = []

    for required in REQUIRED_FILES:
        if not (task_dir / required).is_file():
            missing.append(required)

    if missing:
        failed.append((task_dir.relative_to(ROOT), missing))
        print(f"FAIL: {task_dir.relative_to(ROOT)}")
        for item in missing:
            print(f"  missing: {item}")
    else:
        print(f"PASS: {task_dir.relative_to(ROOT)}")

print()

if failed:
    print(f"Validation failed: {len(failed)} task(s) have missing files.")
    sys.exit(1)

print(f"SUCCESS: All {len(task_files)} tasks have the required structure.")
