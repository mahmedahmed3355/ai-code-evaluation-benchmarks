#!/usr/bin/env bash

set -euo pipefail

ROOT="/app"

echo "=== GPU KERNEL PERFORMANCE VALIDATION ==="

echo "[1/3] Building execution artifact..."

"$ROOT/scripts/build.sh"

echo "[2/3] Verifying generated artifact..."

ARTIFACT="$ROOT/artifacts/kernel_build.artifact"

if [[ ! -s "$ARTIFACT" ]]; then
    echo "ERROR: generated artifact is missing or empty." >&2
    exit 1
fi

echo "Artifact verified: $ARTIFACT"

echo "[3/3] Running correctness and performance benchmark..."

if "$ROOT/scripts/benchmark.sh"; then
    echo "STATUS=PASS"
    echo "VALIDATION=PASS"
    echo "GPU kernel performance validation completed successfully."
    exit 0
else
    echo "STATUS=REGRESSION"
    echo "VALIDATION=FAIL"
    exit 1
fi
