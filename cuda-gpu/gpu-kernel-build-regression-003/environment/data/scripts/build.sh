#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
BUILD_DIR="$ROOT/build"
ARTIFACT_DIR="$ROOT/artifacts"

mkdir -p "$BUILD_DIR" "$ARTIFACT_DIR"

echo "[1/3] Resolving build configuration..."

"$ROOT/scripts/resolve_config.py"

echo "[2/3] Preparing effective configuration..."

cp \
    "$BUILD_DIR/resolved_config.txt" \
    "$BUILD_DIR/effective_config.txt"

echo "[3/3] Generating build artifact..."

python3 "$ROOT/scripts/generate_artifact.py" \
    "$BUILD_DIR/effective_config.txt" \
    "$ARTIFACT_DIR/kernel_build.artifact"

echo "Build completed successfully."
echo "Artifact: $ARTIFACT_DIR/kernel_build.artifact"
