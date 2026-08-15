# CUDA Reduction Correctness Debugging

A CUDA reduction kernel in `/app/src/reduction.cu` is producing incorrect results for some input sizes.

Your task is to diagnose and fix the CUDA correctness issue.

## Problem

The program computes the sum of an input array using a CUDA parallel reduction.

The implementation is expected to produce the exact same result as a CPU reference implementation.

The current implementation passes some small and well-aligned inputs, but fails for certain input sizes and configurations.

Do not assume that the failure is caused by the final reduction operation alone. Inspect the complete execution path, including the CUDA kernel and its launcher.

## Requirements

Fix the underlying correctness bug in the CUDA implementation.

Your solution must:

- Preserve the existing reduction algorithm.
- Preserve the existing kernel interface.
- Preserve the existing launch configuration.
- Preserve the input and output data types.
- Preserve the CUDA implementation; do not replace it with a CPU implementation.
- Correctly handle input sizes that are not multiples of the block size.
- Correctly handle inputs larger than a single CUDA block.
- Produce the exact expected result for all provided test cases.

Do not modify the test files.

Do not modify the expected/reference outputs.

Do not hardcode results for particular input sizes.

Do not skip or remove test cases.

## Investigation

Start by inspecting the files under `/app/src`.

You may run the provided tests and inspect the implementation as needed.

The failure may not be immediately obvious from a single test case. Use multiple input sizes to reproduce and reason about the correctness issue.

Pay particular attention to:

- shared-memory accesses,
- synchronization between reduction stages,
- thread participation,
- boundary conditions,
- block-level versus grid-level reduction,
- and assumptions about input sizes.

## Validation

After making your fix, run:

```bash
/app/run_tests.sh
