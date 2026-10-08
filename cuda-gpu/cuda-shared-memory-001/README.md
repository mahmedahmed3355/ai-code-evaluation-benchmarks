# CUDA Shared-Memory Histogram Reliability Repair

A production-style CUDA debugging task focused on synchronization across multiple phases of a shared-memory histogram kernel.

## Scenario

A data-processing kernel builds a block-local histogram in shared memory, reduces that histogram to a block total, and publishes the block contribution to global memory. The implementation has incorrect phase ordering around shared-memory reads and the block-local reduction.

The repair must preserve the CUDA algorithm while making its synchronization correct for multi-warp execution.

## What the agent must reason about

- Shared-memory visibility after atomic updates
- Block-wide synchronization versus warp-synchronous assumptions
- Distributed shared-memory reduction
- Unconditional `__syncthreads()` participation
- Ordering between local reduction and global publication
- Correct behavior for zero-length input
- Preservation of the original kernel interface and data path

## Evaluation

The verifier checks the source structure and synchronization invariants independently from the task instructions. It rejects CPU or host-side replacements, removal of the shared histogram, changed kernel interfaces, unsafe barrier placement, and incomplete phase ordering.

## Environment

- CPU-only validation container
- No external services
- No network dependency at validation time
- CUDA source is evaluated statically because the benchmark environment does not require a physical GPU

## Author

Mohamed Ahmed — engmohamedelshrbeny@gmail.com

Forge Bench
