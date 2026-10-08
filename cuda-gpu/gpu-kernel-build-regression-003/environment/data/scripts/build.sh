#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
BUILD_DIR="$ROOT/build"
ARTIFACT_DIR="$ROOT/artifacts"

mkdir -p "$BUILD_DIR" "$ARTIFACT_DIR" "$BUILD_DIR/cache"

"$ROOT/scripts/resolve_config.py"
cp "$BUILD_DIR/resolved_config.txt" "$BUILD_DIR/effective_config.txt"
python3 "$ROOT/scripts/generate_artifact.py"     "$BUILD_DIR/effective_config.txt"     "$ARTIFACT_DIR/kernel_build.artifact"

echo "Build completed successfully."
echo "Artifact: $ARTIFACT_DIR/kernel_build.artifact"
