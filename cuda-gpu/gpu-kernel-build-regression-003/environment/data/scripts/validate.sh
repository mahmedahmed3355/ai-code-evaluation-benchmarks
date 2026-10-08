#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"

"$ROOT/scripts/build.sh"
"$ROOT/scripts/diagnose.py"
"$ROOT/scripts/benchmark.sh"

echo "VALIDATION=PASS"
