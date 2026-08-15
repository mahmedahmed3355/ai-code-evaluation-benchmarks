#!/bin/bash
set -euo pipefail

PLAN="/app/build/execution_plan.txt"
REPORT="/app/reports/benchmark.txt"

mkdir -p /app/reports

total=$(grep '^TOTAL_WORK_UNITS=' "$PLAN" | cut -d= -f2)
budget=$(grep '^MAX_WORK_UNITS=' /app/build/resolved_config.txt | cut -d= -f2)

if [ "$total" -le "$budget" ]; then
    score=100
    status="PASS"
else
    score=0
    status="REGRESSION"
fi

cat > "$REPORT" <<REPORT
STATUS=$status
TOTAL_WORK_UNITS=$total
PERFORMANCE_BUDGET=$budget
SCORE=$score
REPORT=benchmark
REPORT
