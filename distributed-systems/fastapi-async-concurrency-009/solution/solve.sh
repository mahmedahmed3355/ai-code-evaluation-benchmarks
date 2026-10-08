#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

path = Path("/app/data/app.py")
source = path.read_text(encoding="utf-8")

if "import asyncio" not in source:
    source = source.replace("import time\n", "import asyncio\nimport time\n", 1)

old = "    delay_ms = blocking_operation(request.delay_ms)\n"
new = '''    delay_ms = await asyncio.to_thread(
        blocking_operation,
        request.delay_ms,
    )
'''

if old not in source:
    raise SystemExit("Expected blocking call was not found.")

path.write_text(source.replace(old, new, 1), encoding="utf-8")
print("Applied event-loop blocking repair.")
PY
