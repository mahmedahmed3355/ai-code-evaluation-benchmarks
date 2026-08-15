#!/bin/bash
set -euo pipefail

echo "=== CUDA MEMORY POOL VALIDATION ==="

echo "[1/3] Building execution artifact..."
/app/scripts/build.sh

echo "[2/3] Verifying generated artifact..."

test -s /app/artifacts/kernel_build.artifact
test -s /app/build/execution_plan.txt
test -s /app/build/resolved_config.txt

echo "Artifact verified: /app/artifacts/kernel_build.artifact"

echo "[3/3] Running performance benchmark..."

if /app/scripts/benchmark.sh; then
    echo "STATUS=PASS"
    echo "VALIDATION=PASS"
else
    echo "STATUS=REGRESSION"
    echo "VALIDATION=FAIL"
    exit 1
fi

echo "CUDA memory pool validation completed successfully."
