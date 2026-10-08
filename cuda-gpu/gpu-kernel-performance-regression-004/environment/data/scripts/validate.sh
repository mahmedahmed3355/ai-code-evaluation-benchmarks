#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
"$ROOT/scripts/build.sh"

if [[ ! -s "$ROOT/artifacts/kernel_build.artifact" ]]; then
    echo "ERROR: generated artifact is missing or empty." >&2
    exit 1
fi

"$ROOT/scripts/benchmark.sh"
echo "STATUS=PASS"
echo "VALIDATION=PASS"
