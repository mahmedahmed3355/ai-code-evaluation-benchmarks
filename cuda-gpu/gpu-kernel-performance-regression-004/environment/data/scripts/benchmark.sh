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

for key in PROFILE STRATEGY BLOCK_SIZE CHUNK_SIZE VECTOR_WIDTH FAST_PATH WORK_UNIT_COST TOTAL_WORK_UNITS CONFIG_SHA256 PLAN_SHA256; do
    if [[ -z "${values[$key]:-}" ]]; then
        echo "ERROR: artifact is missing $key" >&2
        exit 1
    fi
done

CONFIG_DIGEST="$(sha256sum "$ROOT/build/resolved_config.txt" | awk '{print $1}')"
PLAN_DIGEST="$(sha256sum "$ROOT/build/execution_plan.txt" | awk '{print $1}')"

if [[ "${values[CONFIG_SHA256]}" != "$CONFIG_DIGEST" ]]; then
    echo "ERROR: configuration provenance mismatch." >&2
    exit 1
fi
if [[ "${values[PLAN_SHA256]}" != "$PLAN_DIGEST" ]]; then
    echo "ERROR: execution-plan provenance mismatch." >&2
    exit 1
fi

declare -A plan_values
while IFS='=' read -r key value; do
    [[ -z "$key" ]] && continue
    [[ "$key" =~ ^# ]] && continue
    plan_values["$key"]="$value"
done < "$ROOT/build/execution_plan.txt"

if [[ "${values[TOTAL_WORK_UNITS]}" != "${plan_values[TOTAL_WORK_UNITS]:-}" ]]; then
    echo "ERROR: artifact does not match execution plan." >&2
    exit 1
fi

for index in 1 2 3; do
    for suffix in ID INPUT_SIZE PROFILE BUDGET_KEY WORK_UNITS; do
        key="WORKLOAD_${index}_${suffix}"
        if [[ "${values[$key]:-}" != "${plan_values[$key]:-}" ]]; then
            echo "ERROR: artifact workload metadata mismatch." >&2
            exit 1
        fi
    done
done

source "$ROOT/configs/benchmark.conf"

score=100
status="PASS"

[[ "${values[PROFILE]}" == "$REQUIRED_PROFILE" ]] || score=$((score - 25))
[[ "${values[STRATEGY]}" == "blocked" ]] || score=$((score - 25))
[[ "${values[BLOCK_SIZE]}" == "256" ]] || score=$((score - 10))
[[ "${values[CHUNK_SIZE]}" == "4096" ]] || score=$((score - 10))
[[ "${values[VECTOR_WIDTH]}" == "4" ]] || score=$((score - 10))
[[ "${values[FAST_PATH]}" == "1" ]] || score=$((score - 10))
[[ "${values[WORK_UNIT_COST]}" == "1" ]] || score=$((score - 10))

if ! [[ "${values[TOTAL_WORK_UNITS]}" =~ ^[0-9]+$ ]]; then
    echo "ERROR: invalid TOTAL_WORK_UNITS." >&2
    exit 1
fi

(( values[TOTAL_WORK_UNITS] <= AGGREGATE_WORK_BUDGET )) || score=$((score - 20))
(( score < 0 )) && score=0
(( score == 100 )) || status="REGRESSION"

cat > "$REPORT" <<EOF
GPU_KERNEL_PERFORMANCE_REPORT
PROFILE=${values[PROFILE]}
STRATEGY=${values[STRATEGY]}
BLOCK_SIZE=${values[BLOCK_SIZE]}
CHUNK_SIZE=${values[CHUNK_SIZE]}
VECTOR_WIDTH=${values[VECTOR_WIDTH]}
FAST_PATH=${values[FAST_PATH]}
WORK_UNIT_COST=${values[WORK_UNIT_COST]}
TOTAL_WORK_UNITS=${values[TOTAL_WORK_UNITS]}
PERFORMANCE_BUDGET=${AGGREGATE_WORK_BUDGET}
SCORE=$score
STATUS=$status
EOF

echo "Benchmark completed."
echo "Total work units: ${values[TOTAL_WORK_UNITS]}"
echo "Performance budget: ${AGGREGATE_WORK_BUDGET}"
echo "Score: $score"
echo "STATUS=$status"

if [[ "$status" != "PASS" ]]; then
    exit 1
fi
