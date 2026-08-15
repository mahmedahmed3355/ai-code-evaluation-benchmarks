#!/usr/bin/env bash

set -euo pipefail

TARGET="/app/scripts/resolve_config.py"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()

old = """    for _, values in load_all_configs():
        resolved.update(values)
"""

new = """    configs = load_all_configs()

    # Legacy local overrides are retained for diagnostics and compatibility,
    # but they must not override the release performance contract.
    for name, values in configs:
        if name == "local.override":
            continue

        resolved.update(values)
"""

if old not in source:
    raise SystemExit(
        "Expected configuration resolution loop was not found"
    )

path.write_text(source.replace(old, new))
PY

echo "Fixed performance configuration precedence."
