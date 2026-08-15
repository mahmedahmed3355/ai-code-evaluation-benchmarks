#!/bin/bash
set -euo pipefail

echo "[1/3] Resolving configuration..."
python3 /app/scripts/resolve_config.py

echo "[2/3] Generating execution plan..."
python3 /app/scripts/generate_plan.py

echo "[3/3] Generating artifact..."
python3 /app/scripts/generate_artifact.py

echo "Build completed successfully."
