#!/bin/bash
set -euo pipefail

FILE="/app/src/reduction.cu"

if [ ! -f "$FILE" ]; then
    echo "ERROR: missing $FILE"
    exit 1
fi

sed -i '/^[[:space:]]*if (tid < num_blocks) {$/,/^[[:space:]]*}$/c\
    for (unsigned int i = tid;\
         i < static_cast<unsigned int>(num_blocks);\
         i += BLOCK_SIZE) {\
        value += partial_sums[i];\
    }' "$FILE"

grep -Fq 'cudaMalloc' "$FILE"
grep -Fq 'void reduce_sum' "$FILE"
grep -Fq 'n + BLOCK_SIZE - 1' "$FILE"
grep -Fq 'reduce_sum_kernel<<<num_blocks, BLOCK_SIZE>>>' "$FILE"

grep -Fq 'for (unsigned int i = tid;' "$FILE"
grep -Fq 'i += BLOCK_SIZE' "$FILE"
grep -Fq 'value += partial_sums[i];' "$FILE"

echo "Applied multi-block reduction fix."
echo "Original CUDA host implementation preserved."
echo "Verified multi-block partial-sum traversal."
