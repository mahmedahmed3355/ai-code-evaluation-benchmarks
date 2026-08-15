#!/usr/bin/env bash
set -euo pipefail

cd /app

if [[ ! -f /app/src/reduction.cu ]]; then
    echo "ERROR: missing /app/src/reduction.cu" >&2
    exit 1
fi

if [[ ! -f /app/src/reduction_test.cu ]]; then
    echo "ERROR: missing /app/src/reduction_test.cu" >&2
    exit 1
fi

nvcc \
    -O2 \
    -std=c++17 \
    /app/src/reduction.cu \
    /app/src/reduction_test.cu \
    -o /app/reduction_test

exec /app/reduction_test
