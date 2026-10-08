#!/usr/bin/env bash
set -euo pipefail

cat > /app/scripts/resolve_config.py <<'PY'
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
OUTPUT = ROOT / "build" / "resolved_config.txt"

PROTECTED = {
    "BUILD_TYPE",
    "OPT_LEVEL",
    "FAST_MATH",
    "VECTOR_WIDTH",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
}


def load_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    base = load_config(CONFIG_DIR / "build.conf")
    profile = load_config(CONFIG_DIR / "release.profile")
    benchmark = load_config(CONFIG_DIR / "benchmark.conf")
    local = load_config(CONFIG_DIR / "local.override")

    config = dict(base)
    config.update(profile)

    for key, value in local.items():
        if key not in PROTECTED:
            config[key] = value

    for key in benchmark:
        if key not in config:
            config[key] = benchmark[key]

    OUTPUT.write_text("".join(f"{key}={value}\n" for key, value in sorted(config.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

PY

cat > /app/scripts/benchmark.sh <<'SH'
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

SH

chmod +x /app/scripts/resolve_config.py /app/scripts/benchmark.sh
echo "Reference repair applied."
