#!/bin/bash
set -euo pipefail

CONFIG="/app/configs/local.override"

python3 - "$CONFIG" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])

values = {}

for line in path.read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#") or "=" not in line:
        continue

    key, value = line.split("=", 1)
    values[key.strip()] = value.strip()

# Restore the optimized memory-access strategy.
required = {
    "BLOCK_SIZE": "256",
    "VECTOR_WIDTH": "4",
    "COALESCED_ACCESS": "1",
    "ALIGNED_ACCESS": "1",
    "FAST_PATH": "1",
    "CHUNK_SIZE": "4096",
}

values.update(required)

with path.open("w") as f:
    f.write("# Local developer override\n")
    f.write("# Restored optimized memory-access configuration.\n")

    for key in [
        "BLOCK_SIZE",
        "VECTOR_WIDTH",
        "COALESCED_ACCESS",
        "ALIGNED_ACCESS",
        "FAST_PATH",
        "CHUNK_SIZE",
    ]:
        f.write(f"{key}={values[key]}\n")

print("Restored optimized memory-access configuration.")
PY

/app/scripts/validate.sh
