#!/bin/bash
set -euo pipefail

PLAN="/app/build/execution_plan.txt"
CONFIG="/app/build/resolved_config.txt"
REPORT="/app/reports/benchmark.txt"

mkdir -p /app/reports

get_value() {
    grep "^$1=" "$2" | cut -d= -f2-
}

TOTAL=$(get_value TOTAL_WORK_UNITS "$PLAN")
BUDGET=$(get_value PERFORMANCE_BUDGET "$CONFIG")

if [ "$TOTAL" -le "$BUDGET" ]; then
    STATUS="PASS"
    SCORE=100
else
    STATUS="REGRESSION"
    SCORE=0
fi

cat > "$REPORT" <<REPORT
STATUS=$STATUS
TOTAL_WORK_UNITS=$TOTAL
PERFORMANCE_BUDGET=$BUDGET
SCORE=$SCORE
REPORT=benchmark
REPORT

echo "STATUS=$STATUS"
echo "TOTAL_WORK_UNITS=$TOTAL"
echo "PERFORMANCE_BUDGET=$BUDGET"
echo "SCORE=$SCORE"
echo "REPORT=benchmark"

if [ "$STATUS" != "PASS" ]; then
    exit 1
fi
