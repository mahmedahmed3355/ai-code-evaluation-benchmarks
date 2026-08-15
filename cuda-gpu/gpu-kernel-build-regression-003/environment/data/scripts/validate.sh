#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"

echo "=== GPU BUILD VALIDATION ==="

echo "[1/3] Building artifact..."
"$ROOT/scripts/build.sh"

echo "[2/3] Inspecting generated configuration..."
"$ROOT/scripts/diagnose.py"

echo "[3/3] Running benchmark contract..."
if "$ROOT/scripts/benchmark.sh"; then
    echo "VALIDATION=PASS"
else
    echo "VALIDATION=FAIL"
    exit 1
fi

echo
echo "GPU build validation completed successfully."
