#!/usr/bin/env bash

set -euo pipefail

ROOT="/app"
BUILD_DIR="$ROOT/build"
ARTIFACT_DIR="$ROOT/artifacts"

mkdir -p "$BUILD_DIR" "$ARTIFACT_DIR"

echo "[1/4] Resolving configuration..."

python3 "$ROOT/scripts/resolve_config.py"

echo "[2/4] Generating execution plan..."

python3 "$ROOT/scripts/generate_plan.py"

echo "[3/4] Generating artifact..."

python3 "$ROOT/scripts/generate_artifact.py"

echo "[4/4] Build completed."

echo "Artifact: $ARTIFACT_DIR/kernel_build.artifact"
