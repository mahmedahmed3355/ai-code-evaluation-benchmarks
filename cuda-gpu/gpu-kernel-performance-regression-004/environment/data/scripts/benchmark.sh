#!/usr/bin/env bash

set -euo pipefail

ROOT="/app"
ARTIFACT="$ROOT/artifacts/kernel_build.artifact"
REPORT_DIR="$ROOT/reports"
REPORT="$REPORT_DIR/benchmark.txt"

mkdir -p "$REPORT_DIR"

if [[ ! -f "$ARTIFACT" ]]; then
    echo "ERROR: build artifact is missing." >&2
    exit 1
fi

declare -A values

while IFS='=' read -r key value; do
    [[ -z "$key" ]] && continue
    [[ "$key" =~ ^# ]] && continue
    values["$key"]="$value"
done < "$ARTIFACT"

required_keys=(
    BUILD_TYPE
    OPT_LEVEL
    STRATEGY
    BLOCK_SIZE
    CHUNK_SIZE
    VECTOR_WIDTH
    FAST_PATH
    WORK_UNIT_COST
    ARTIFACT_MODE
    TOTAL_WORK_UNITS
)

for key in "${required_keys[@]}"; do
    if [[ -z "${values[$key]:-}" ]]; then
        echo "ERROR: artifact is missing $key" >&2
        exit 1
    fi
done

BUILD_TYPE="${values[BUILD_TYPE]}"
OPT_LEVEL="${values[OPT_LEVEL]}"
STRATEGY="${values[STRATEGY]}"
BLOCK_SIZE="${values[BLOCK_SIZE]}"
CHUNK_SIZE="${values[CHUNK_SIZE]}"
VECTOR_WIDTH="${values[VECTOR_WIDTH]}"
FAST_PATH="${values[FAST_PATH]}"
WORK_UNIT_COST="${values[WORK_UNIT_COST]}"
ARTIFACT_MODE="${values[ARTIFACT_MODE]}"
TOTAL_WORK_UNITS="${values[TOTAL_WORK_UNITS]}"

PERFORMANCE_BUDGET=500000

score=100

if [[ "$OPT_LEVEL" != "3" ]]; then
    score=$((score - 15))
fi

if [[ "$STRATEGY" != "blocked" ]]; then
    score=$((score - 25))
fi

if [[ "$BLOCK_SIZE" != "256" ]]; then
    score=$((score - 10))
fi

if [[ "$CHUNK_SIZE" != "4096" ]]; then
    score=$((score - 10))
fi

if [[ "$VECTOR_WIDTH" != "4" ]]; then
    score=$((score - 10))
fi

if [[ "$FAST_PATH" != "1" ]]; then
    score=$((score - 10))
fi

if [[ "$WORK_UNIT_COST" != "1" ]]; then
    score=$((score - 10))
fi

if [[ "$ARTIFACT_MODE" != "optimized" ]]; then
    score=$((score - 10))
fi

if ! [[ "$TOTAL_WORK_UNITS" =~ ^[0-9]+$ ]]; then
    echo "ERROR: invalid TOTAL_WORK_UNITS." >&2
    exit 1
fi

if (( TOTAL_WORK_UNITS > PERFORMANCE_BUDGET )); then
    score=$((score - 20))
fi

if (( score < 0 )); then
    score=0
fi

if (( score == 100 && TOTAL_WORK_UNITS <= PERFORMANCE_BUDGET )); then
    status="PASS"
else
    status="REGRESSION"
fi

cat > "$REPORT" <<EOF
GPU_KERNEL_PERFORMANCE_REPORT
BUILD_TYPE=$BUILD_TYPE
OPT_LEVEL=$OPT_LEVEL
STRATEGY=$STRATEGY
BLOCK_SIZE=$BLOCK_SIZE
CHUNK_SIZE=$CHUNK_SIZE
VECTOR_WIDTH=$VECTOR_WIDTH
FAST_PATH=$FAST_PATH
WORK_UNIT_COST=$WORK_UNIT_COST
TOTAL_WORK_UNITS=$TOTAL_WORK_UNITS
PERFORMANCE_BUDGET=$PERFORMANCE_BUDGET
SCORE=$score
STATUS=$status
EOF

echo "Benchmark completed."
echo "Total work units: $TOTAL_WORK_UNITS"
echo "Performance budget: $PERFORMANCE_BUDGET"
echo "Score: $score"
echo "Report: $REPORT"
echo "STATUS=$status"

if [[ "$status" != "PASS" ]]; then
    exit 1
fi
