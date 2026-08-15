#!/bin/bash
set -euo pipefail

echo "[1/3] Resolving configuration..."
/app/scripts/resolve_config.py

echo "[2/3] Generating execution plan..."
/app/scripts/generate_plan.py

echo "[3/3] Generating artifact..."
/app/scripts/generate_artifact.py

echo "Build completed successfully."
