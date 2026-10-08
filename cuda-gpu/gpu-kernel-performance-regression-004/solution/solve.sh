#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/scripts/resolve_config.py")
source = path.read_text()
old = '    resolved.update(configs["local.override"])\n'
new = """    for key, value in configs["local.override"].items():
        if key not in PROTECTED_KEYS:
            resolved[key] = value
"""
if old not in source:
    raise SystemExit("expected resolver behavior was not found")
path.write_text(source.replace(old, new))
PY
