#!/usr/bin/env bash
set -euo pipefail

SOURCE=/app/src/broken_kernel.cu
python3 - "$SOURCE" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")

needle = '''    for (int i = blockIdx.x * blockDim.x + threadIdx.x;
         i < n;
         i += blockDim.x * gridDim.x) {
        atomicAdd(&histogram[input[i]], 1U);
    }

    if (threadIdx.x == 0) {
'''
replacement = '''    for (int i = blockIdx.x * blockDim.x + threadIdx.x;
         i < n;
         i += blockDim.x * gridDim.x) {
        atomicAdd(&histogram[input[i]], 1U);
    }

    __syncthreads();

    if (threadIdx.x == 0) {
'''
if needle not in source:
    raise SystemExit("accumulation phase not found")
source = source.replace(needle, replacement, 1)

old = '''    if (threadIdx.x == 0) {
        for (int bin = 0; bin < HISTOGRAM_BINS; ++bin) {
            block_total += histogram[bin];
        }
    }
'''
new = '''    unsigned int local_total = 0;
    for (int bin = threadIdx.x;
         bin < HISTOGRAM_BINS;
         bin += blockDim.x) {
        local_total += histogram[bin];
    }
    atomicAdd(&block_total, local_total);

    __syncthreads();
'''
if old not in source:
    raise SystemExit("shared reduction phase not found")
source = source.replace(old, new, 1)

path.write_text(source, encoding="utf-8")
PY
