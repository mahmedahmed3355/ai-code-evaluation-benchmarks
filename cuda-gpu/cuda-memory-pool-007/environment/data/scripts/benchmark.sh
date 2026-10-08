#!/bin/bash
set -euo pipefail
PLAN="/app/build/execution_plan.txt"
CONFIG="/app/build/resolved_config.txt"
REPORT="/app/reports/benchmark.txt"
mkdir -p /app/reports
get_value() { grep "^$1=" "$2" | cut -d= -f2-; }
TOTAL=$(get_value TOTAL_WORK_UNITS "$PLAN")
BUDGET=$(get_value PERFORMANCE_BUDGET "$CONFIG")
declare -A LIMITS=(
  [small]=$(get_value SMALL_WORK_BUDGET /app/configs/benchmark.conf)
  [medium]=$(get_value MEDIUM_WORK_BUDGET /app/configs/benchmark.conf)
  [large]=$(get_value LARGE_WORK_BUDGET /app/configs/benchmark.conf)
  [burst]=$(get_value BURST_WORK_BUDGET /app/configs/benchmark.conf)
  [reuse-heavy]=$(get_value REUSE_HEAVY_WORK_BUDGET /app/configs/benchmark.conf)
)
STATUS="PASS"
for i in 1 2 3 4 5; do
  name=$(get_value WORKLOAD_${i}_NAME "$PLAN")
  work=$(get_value WORKLOAD_${i}_WORK_UNITS "$PLAN")
  limit=${LIMITS[$name]}
  if [ "$work" -gt "$limit" ]; then STATUS="REGRESSION"; fi
done
if [ "$TOTAL" -gt "$BUDGET" ]; then STATUS="REGRESSION"; fi
SCORE=0
[ "$STATUS" = "PASS" ] && SCORE=100
{
  echo "STATUS=$STATUS"
  echo "TOTAL_WORK_UNITS=$TOTAL"
  echo "PERFORMANCE_BUDGET=$BUDGET"
  echo "SMALL_WORK_BUDGET=${LIMITS[small]}"
  echo "MEDIUM_WORK_BUDGET=${LIMITS[medium]}"
  echo "LARGE_WORK_BUDGET=${LIMITS[large]}"
  echo "BURST_WORK_BUDGET=${LIMITS[burst]}"
  echo "REUSE_HEAVY_WORK_BUDGET=${LIMITS[reuse-heavy]}"
  echo "SCORE=$SCORE"
  echo "REPORT=benchmark"
} | tee "$REPORT"
[ "$STATUS" = "PASS" ]
