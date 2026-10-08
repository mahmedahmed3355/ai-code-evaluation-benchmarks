#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
mkdir -p "$ROOT/build" "$ROOT/artifacts" "$ROOT/reports"
python3 "$ROOT/scripts/resolve_config.py"
python3 "$ROOT/scripts/generate_plan.py"
python3 "$ROOT/scripts/generate_artifact.py"
