#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/app/src/broken_kernel.cu"
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if not SOURCE.is_file():
        fail(f"source file not found: {SOURCE}")

    source = SOURCE.read_text(encoding="utf-8")

    # The task must remain a CUDA kernel using shared memory.
    if "__global__" not in source:
        fail("CUDA kernel declaration is missing")

    if "__shared__" not in source:
        fail("shared memory usage is missing")

    if "atomicAdd" not in source:
        fail("atomicAdd-based histogram update is missing")

    # The kernel interface must remain unchanged.
    signature = re.compile(
        r"__global__\s+void\s+shared_histogram_kernel\s*"
        r"\(\s*"
        r"const\s+unsigned\s+char\s*\*\s*input\s*,\s*"
        r"unsigned\s+int\s*\*\s*output\s*,\s*"
        r"int\s+n\s*"
        r"\)",
        re.MULTILINE,
    )

    if not signature.search(source):
        fail("kernel signature was changed")

    # Locate the accumulation loop.
    accumulation = source.find("atomicAdd(&histogram[input[i]], 1U);")

    if accumulation == -1:
        fail("input accumulation statement not found")

    # Locate the final consumption of shared memory.
    final_consume = source.find(
        "atomicAdd(&output[bin], histogram[bin]);"
    )

    if final_consume == -1:
        fail("final histogram accumulation not found")

    if accumulation >= final_consume:
        fail("unexpected ordering of histogram operations")

    # The required synchronization must occur after all shared-memory
    # producers and before the shared-memory consumer loop.
    barrier = source.find("__syncthreads();", accumulation)

    if barrier == -1:
        fail(
            "missing __syncthreads() after the shared-memory "
            "accumulation phase"
        )

    if barrier > final_consume:
        fail(
            "__syncthreads() occurs after the shared-memory "
            "consumer phase"
        )

    # Ensure the synchronization is not merely the initialization barrier.
    barriers = [
        match.start()
        for match in re.finditer(r"\b__syncthreads\s*\(\s*\)", source)
    ]

    if len(barriers) < 2:
        fail(
            "the kernel needs a second synchronization barrier "
            "between production and consumption"
        )

    print("PASS: shared-memory synchronization fix detected")


if __name__ == "__main__":
    main()
