# CUDA Reduction Correctness Repair

Repair the CUDA reduction implementation in `/app/src/reduction.cu`.

The program computes the sum of a floating-point input array in two stages. The first kernel produces one partial sum per block. The second kernel combines those partial sums.

The implementation is intentionally close to a working implementation, but it contains correctness failures that only become visible at important boundary conditions.

## Required behavior

`reduce_sum` must:

- return the sum of every input element;
- return `0.0f` for an empty input (`n == 0`);
- work when `n` is smaller than one block;
- work when `n` is exactly a block boundary;
- work when `n` is just above a block boundary;
- work when the number of partial sums is greater than `BLOCK_SIZE`;
- work when the number of partial sums is not a multiple of `BLOCK_SIZE`;
- preserve the existing two-stage CUDA reduction design.

The supplied executable exercises all of these cases.

## Constraints

Do not modify the test files.

Do not modify the kernel interfaces:

- `reduce_sum_kernel`
- `finalize_sum_kernel`
- `reduce_sum`

Keep `BLOCK_SIZE` at 256.

Keep the existing launch configuration:

- `reduce_sum_kernel<<<num_blocks, BLOCK_SIZE>>>`
- `finalize_sum_kernel<<<1, BLOCK_SIZE>>>`

Keep the existing input and output types.

Keep the implementation on the GPU. Do not replace the reduction with CPU code, a host-side accumulation, a library reduction, or a different high-level framework.

Do not hard-code answers or special-case the supplied test sizes.

Do not remove the first-stage block reduction.

Do not replace the final shared-memory reduction with a serial host computation.

Do not modify the expected/reference test behavior.

## Investigation guidance

Do not assume that the visible failure has only one cause.

Trace the complete path from `n` to:

1. the number of first-stage blocks,
2. the allocation of the partial-sum buffer,
3. the values produced by each first-stage block,
4. the values loaded by the final kernel,
5. the final shared-memory reduction,
6. the zero-length input case.

In particular, reason about the relationship between `num_blocks` and `BLOCK_SIZE`. The final kernel has a fixed number of threads, while the number of partial sums is derived from the input size.

A correct repair must remain valid when `num_blocks` is larger than the number of threads in the final kernel.

Also consider what a zero-block launch means when `n == 0`. The caller expects a valid reduction result rather than a CUDA launch failure.

## Validation

From `/app`, run:

```bash
./run_reduction.sh
```

The program compares the GPU result with a CPU reference across small inputs, block boundaries, multi-block inputs, and inputs large enough to create more than 256 partial sums.

Do not change the validation program to make the implementation appear correct.
