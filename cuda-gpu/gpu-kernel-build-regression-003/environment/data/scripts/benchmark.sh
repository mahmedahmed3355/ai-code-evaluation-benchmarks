#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
ARTIFACT="$ROOT/artifacts/kernel_build.artifact"
CONFIG="$ROOT/build/effective_config.txt"
CONTRACT="$ROOT/reference/optimization_contract.txt"
REPORT="$ROOT/reports/benchmark.txt"

mkdir -p "$ROOT/reports"

if [[ ! -f "$ARTIFACT" || ! -f "$CONFIG" || ! -f "$CONTRACT" ]]; then
    echo "ERROR: validation inputs are missing." >&2
    exit 1
fi

python3 - "$ARTIFACT" "$CONFIG" "$CONTRACT" "$REPORT" <<'PY'
import hashlib
import sys
from pathlib import Path

artifact_path, config_path, contract_path, report_path = map(Path, sys.argv[1:])

def parse(path):
    out = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            out[key.strip()] = value.strip()
    return out

artifact = parse(artifact_path)
config = parse(config_path)
contract = parse(contract_path)

keys = (
    "BUILD_TYPE",
    "OPT_LEVEL",
    "FAST_MATH",
    "VECTOR_WIDTH",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
)

canonical = "".join(f"{key}={config.get(key, '')}\n" for key in keys)
expected_digest = hashlib.sha256(canonical.encode()).hexdigest()

score = 100
failures = []

if artifact.get("CONFIG_SHA256") != expected_digest:
    failures.append("artifact provenance mismatch")

for key in keys:
    if artifact.get(key) != config.get(key):
        failures.append(f"artifact/config mismatch: {key}")

for key in ("BUILD_TYPE", "OPT_LEVEL", "FAST_MATH", "VECTOR_WIDTH", "DEBUG_SYMBOLS", "LTO", "ARTIFACT_MODE"):
    expected = contract.get(key)
    if expected is not None and config.get(key) != expected:
        failures.append(f"contract mismatch: {key}")

if config.get("OPT_LEVEL") != "3":
    score -= 35
if config.get("FAST_MATH") != "1":
    score -= 20
if config.get("VECTOR_WIDTH") != "4":
    score -= 25
if config.get("LTO") != "1":
    score -= 20

minimum = int(contract.get("BENCHMARK_SCORE_MIN", "100"))
if score < minimum:
    failures.append(f"score below contract minimum: {score} < {minimum}")

status = "PASS" if not failures else "REGRESSION"

report_path.write_text(
    "GPU_KERNEL_BENCHMARK_REPORT\n"
    f"SCORE={score}\n"
    f"STATUS={status}\n"
    f"FAILURES={len(failures)}\n"
    + "".join(f"FAILURE_{i+1}={item}\n" for i, item in enumerate(failures))
)

if failures:
    print("STATUS=REGRESSION")
    raise SystemExit(1)

print("SCORE=100")
print("STATUS=PASS")
PY
