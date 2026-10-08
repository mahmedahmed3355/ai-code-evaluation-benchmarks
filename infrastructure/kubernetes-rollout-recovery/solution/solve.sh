#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
import os, yaml
D=Path(os.environ.get("TASK_DATA", "/app/data"))
canonical={"app":"inference-api","track":"stable","release":"2026-10"}

p=D/"deployment.yaml"; x=yaml.safe_load(p.read_text())
x["spec"]["selector"]["matchLabels"]=dict(canonical)
x["spec"]["template"]["metadata"]["labels"]=dict(canonical)
p.write_text(yaml.safe_dump(x,sort_keys=False))

p=D/"service.yaml"; x=yaml.safe_load(p.read_text())
x["spec"]["selector"]=dict(canonical)
p.write_text(yaml.safe_dump(x,sort_keys=False))

p=D/"pdb.yaml"; x=yaml.safe_load(p.read_text())
x["spec"]["selector"]["matchLabels"]=dict(canonical)
p.write_text(yaml.safe_dump(x,sort_keys=False))
print("Applied cross-resource workload identity repair.")
PY
TASK_DATA="${TASK_DATA:-/app/data}" python3 "${VALIDATOR:-/app/validate.py}"
