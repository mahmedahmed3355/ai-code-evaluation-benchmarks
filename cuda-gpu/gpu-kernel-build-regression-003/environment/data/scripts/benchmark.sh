#!/usr/bin/env bash
set -euo pipefail

ROOT="/app"
ARTIFACT="$ROOT/artifacts/kernel_build.artifact"
REPORT="$ROOT/reports/benchmark.txt"

mkdir -p "$ROOT/reports"

if [[ ! -f "$ARTIFACT" ]]; then
    echo "ERROR: build artifact is missing." >&2
    exit 1
fi

source <(
    awk -F= '
        /^[A-Z_][A-Z0-9_]*=/ {
            print $1 "=" $2
        }
    ' "$ARTIFACT"
)

: "${OPT_LEVEL:?missing OPT_LEVEL}"
: "${FAST_MATH:?missing FAST_MATH}"
: "${VECTOR_WIDTH:?missing VECTOR_WIDTH}"
: "${LTO:?missing LTO}"

score=100

if [[ "$OPT_LEVEL" -lt 3 ]]; then
    score=$((score - 35))
fi

if [[ "$FAST_MATH" != "1" ]]; then
    score=$((score - 20))
fi

if [[ "$VECTOR_WIDTH" -lt 4 ]]; then
    score=$((score - 25))
fi

if [[ "$LTO" != "1" ]]; then
    score=$((score - 20))
fi

if [[ "$score" -lt 0 ]]; then
    score=0
fi

if [[ "$score" -eq 100 ]]; then
    status="PASS"
else
    status="REGRESSION"
fi

cat > "$REPORT" <<EOF
GPU_KERNEL_BENCHMARK_REPORT
OPT_LEVEL=$OPT_LEVEL
FAST_MATH=$FAST_MATH
VECTOR_WIDTH=$VECTOR_WIDTH
LTO=$LTO
SCORE=$score
STATUS=$status
EOF

echo "Benchmark completed."
echo "Score: $score"
echo "Report: $REPORT"
echo "STATUS=$status"

if [[ "$status" != "PASS" ]]; then
    exit 1
fi
