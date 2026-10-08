#!/usr/bin/env bash
set -euo pipefail

cd /app

test -f /app/src/reduction.cu
test -f /app/src/reduction_test.cu

nvcc -O2 -std=c++17 /app/src/reduction.cu /app/src/reduction_test.cu -o /app/reduction_test

exec /app/reduction_test
