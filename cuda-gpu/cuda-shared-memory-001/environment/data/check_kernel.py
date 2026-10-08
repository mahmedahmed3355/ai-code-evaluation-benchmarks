#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/app/src/broken_kernel.cu")


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if not SOURCE.is_file():
        fail(f"source file not found: {SOURCE}")
    source = SOURCE.read_text(encoding="utf-8")

    if "__global__" not in source or "__shared__" not in source:
        fail("CUDA shared-memory kernel structure is missing")

    signature = re.compile(
        r"__global__\s+void\s+shared_histogram_kernel\s*"
        r"\(\s*const\s+unsigned\s+char\s*\*\s*input\s*,\s*"
        r"unsigned\s+int\s*\*\s*output\s*,\s*int\s+n\s*\)",
        re.MULTILINE,
    )
    if not signature.search(source):
        fail("kernel signature was changed")

    required = [
        "__shared__ unsigned int histogram[HISTOGRAM_BINS];",
        "__shared__ unsigned int block_total;",
        "atomicAdd(&histogram[input[i]], 1U);",
        "unsigned int local_total = 0;",
        "atomicAdd(&block_total, local_total);",
        "atomicAdd(&output[threadIdx.x], histogram[threadIdx.x]);",
        "output[HISTOGRAM_BINS] += block_total;",
    ]
    for token in required:
        if token not in source:
            fail(f"required operation is missing: {token}")

    barriers = [m.start() for m in re.finditer(r"\b__syncthreads\s*\(\s*\)", source)]
    if len(barriers) < 3:
        fail("expected initialization, accumulation, reduction, and publication phase barriers")

    accumulation = source.find("atomicAdd(&histogram[input[i]], 1U);")
    first_reduce = source.find("unsigned int local_total = 0;")
    reduce_atomic = source.find("atomicAdd(&block_total, local_total);")
    global_publish = source.find("atomicAdd(&output[threadIdx.x], histogram[threadIdx.x]);")
    final_publish = source.find("output[HISTOGRAM_BINS] += block_total;")

    if min(accumulation, first_reduce, reduce_atomic, global_publish, final_publish) < 0:
        fail("required phases could not be located")

    if not (accumulation < first_reduce < reduce_atomic < global_publish < final_publish):
        fail("kernel phases are not ordered correctly")

    init_barrier = [p for p in barriers if p < accumulation]
    post_accumulation = [p for p in barriers if accumulation < p < first_reduce]
    post_reduction = [p for p in barriers if reduce_atomic < p < global_publish]
    if not init_barrier:
        fail("missing initialization barrier")
    if not post_accumulation:
        fail("shared histogram can be read before all accumulation writes finish")
    if not post_reduction:
        fail("block_total can be published before all block threads finish the reduction")
    before_first_barrier = source[:init_barrier[-1]]
    if "return" in before_first_barrier:
        fail("early exit before the initialization barrier is unsafe")

    between_barriers = source[post_accumulation[0]:post_reduction[0]]
    if "return" in between_barriers:
        fail("early exit between block-wide synchronization phases is unsafe")

    if re.search(r"if\s*\([^\n{}]*threadIdx\.x[^\n{}]*\)\s*\{[^{}]*__syncthreads", source, re.DOTALL):
        fail("block-wide synchronization is inside a thread-dependent branch")

    if "__threadfence" in source or "cudaDeviceSynchronize" in source:
        fail("unrelated synchronization primitive was introduced as a substitute")

    print("PASS: shared-memory histogram phase ordering and synchronization are valid")


if __name__ == "__main__":
    main()
