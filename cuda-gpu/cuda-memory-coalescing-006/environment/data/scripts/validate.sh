#!/bin/bash
set -euo pipefail
/app/scripts/build.sh
test -s /app/artifacts/kernel_build.artifact
test -s /app/artifacts/kernel_build.provenance
/app/scripts/benchmark.sh
grep -q '^STATUS=PASS$' /app/reports/benchmark.txt
echo VALIDATION=PASS
