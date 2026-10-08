#!/bin/bash
set -euo pipefail
python3 /app/scripts/resolve_config.py
python3 /app/scripts/generate_plan.py
python3 /app/scripts/generate_artifact.py
