#!/bin/bash
set -euo pipefail
echo "=== CUDA MEMORY POOL VALIDATION ==="
echo "[1/3] Building execution artifact..."
/app/scripts/build.sh
echo "[2/3] Verifying generated artifact..."
test -s /app/artifacts/kernel_build.artifact
test -s /app/artifacts/kernel_build.provenance
test -s /app/build/execution_plan.txt
test -s /app/build/resolved_config.txt
test -s /app/build/config_provenance.txt
echo "[3/3] Running performance benchmark..."
/app/scripts/benchmark.sh
echo "STATUS=PASS"
echo "VALIDATION=PASS"
