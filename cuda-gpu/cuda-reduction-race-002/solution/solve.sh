#!/bin/bash
set -euo pipefail

FILE="/app/src/reduction.cu"

python3 - <<'PY'
from pathlib import Path

p = Path("/app/src/reduction.cu")
s = p.read_text()

old = """    float* d_partial = nullptr;

    cudaMalloc(
        &d_partial,
        num_blocks * sizeof(float)
    );
"""
new = """    if (n == 0) {
        cudaMemset(d_output, 0, sizeof(float));
        return;
    }

    float* d_partial = nullptr;

    cudaMalloc(
        &d_partial,
        num_blocks * sizeof(float)
    );
"""
if old not in s:
    raise SystemExit("expected allocation block not found")
s = s.replace(old, new, 1)

old = """    float value = 0.0f;

    if (tid < num_blocks) {
        value = partial_sums[tid];
    }

    shared[tid] = value;
"""
new = """    float value = 0.0f;

    for (unsigned int i = tid;
         i < static_cast<unsigned int>(num_blocks);
         i += BLOCK_SIZE) {
        value += partial_sums[i];
    }

    shared[tid] = value;
"""
if old not in s:
    raise SystemExit("expected final-kernel load block not found")
s = s.replace(old, new, 1)

p.write_text(s)
PY

grep -Fq 'if (n == 0)' "$FILE"
grep -Fq 'cudaMemset(d_output, 0, sizeof(float));' "$FILE"
grep -Fq 'for (unsigned int i = tid;' "$FILE"
grep -Fq 'i < static_cast<unsigned int>(num_blocks)' "$FILE"
grep -Fq 'i += BLOCK_SIZE' "$FILE"
grep -Fq 'value += partial_sums[i];' "$FILE"
grep -Fq 'reduce_sum_kernel<<<num_blocks, BLOCK_SIZE>>>' "$FILE"
grep -Fq 'finalize_sum_kernel<<<1, BLOCK_SIZE>>>' "$FILE"

echo "Reference repair applied."
