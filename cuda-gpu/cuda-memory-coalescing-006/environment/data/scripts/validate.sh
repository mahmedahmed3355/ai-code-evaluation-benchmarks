#!/bin/bash
set -euo pipefail

echo "=== CUDA MEMORY COALESCING VALIDATION ==="

echo "[1/3] Building execution artifact..."
/app/scripts/build.sh

echo "[2/3] Verifying generated artifact..."
test -s /app/artifacts/kernel_build.artifact

echo "[3/3] Running performance benchmark..."
/app/scripts/benchmark.sh

cat /app/reports/benchmark.txt

if grep -q '^STATUS=PASS$' /app/reports/benchmark.txt; then
    echo "VALIDATION=PASS"
else
    echo "VALIDATION=FAIL"
    exit 1
fi
