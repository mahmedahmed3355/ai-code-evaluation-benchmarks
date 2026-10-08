#!/bin/bash
set -euo pipefail

PLAN=/app/build/execution_plan.txt
REPORT=/app/reports/benchmark.txt
CFG=/app/build/resolved_config.txt

total=$(grep '^TOTAL_WORK_UNITS=' "$PLAN" | cut -d= -f2)
budget=$(grep '^MAX_WORK_UNITS=' "$CFG" | cut -d= -f2)

small=$(grep '^WORKLOAD_1_WORK_UNITS=' "$PLAN" | cut -d= -f2)
medium=$(grep '^WORKLOAD_2_WORK_UNITS=' "$PLAN" | cut -d= -f2)
large=$(grep '^WORKLOAD_3_WORK_UNITS=' "$PLAN" | cut -d= -f2)

mkdir -p /app/reports

status=PASS
[ "$total" -le "$budget" ] || status=REGRESSION
[ "$small" -le 12000 ] || status=REGRESSION
[ "$medium" -le 90000 ] || status=REGRESSION
[ "$large" -le 500000 ] || status=REGRESSION

score=0
[ "$status" = PASS ] && score=100

cat > "$REPORT" <<EOF
STATUS=$status
TOTAL_WORK_UNITS=$total
PERFORMANCE_BUDGET=$budget
SMALL_WORK_UNITS=$small
MEDIUM_WORK_UNITS=$medium
LARGE_WORK_UNITS=$large
SCORE=$score
EOF
