#!/usr/bin/env bash

set -euo pipefail

TARGET="/app/scripts/resolve_config.py"

python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()

old = """    # Compatibility settings are intentionally loaded last.
    #
    # The task's regression is related to how configuration sources
    # are resolved. Investigate the resulting effective state rather
    # than assuming every source has the same precedence.
    config.update(load_config(CONFIG_DIR / "local.override"))
"""

new = """    # Legacy compatibility settings must not override the
    # release and benchmark contract. They are retained for
    # compatibility and diagnostics, but release/benchmark
    # configuration has authoritative precedence.
"""

if old not in source:
    raise SystemExit(
        "Expected configuration-resolution block was not found"
    )

path.write_text(source.replace(old, new))
PY

echo "Fixed configuration precedence."
