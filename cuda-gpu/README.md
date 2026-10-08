# CUDA / GPU Engineering

**8 benchmark tasks**

This domain evaluates low-level GPU correctness, asynchronous execution, memory behavior, synchronization, build reproducibility and performance-regression diagnosis.

| Task | Difficulty | Focus |
|---|---|---|
| `cuda-memory-allocator-008` | Hard | Async allocator semantics, stream ordering, memory pools |
| `cuda-memory-coalescing-006` | Hard | Memory-access regression, configuration precedence, provenance |
| `cuda-memory-pool-007` | Hard | Stream-ordered pools, reuse, synchronization, generated artifacts |
| `cuda-reduction-race-002` | Hard | Multi-stage reduction, empty input, partial-sum coverage |
| `cuda-shared-memory-001` | Hard | Shared-memory visibility, barriers, block reduction |
| `cuda-stream-event-dependency` | Hard | Stream/event happens-before dependencies |
| `gpu-kernel-build-regression-003` | Hard | Build configuration, artifact trust, provenance |
| `gpu-kernel-performance-regression-004` | Hard | Performance contracts, workload budgets, regression diagnosis |

## What is tested

The tasks emphasize reasoning about GPU execution semantics rather than superficial source edits. Verification may inspect memory strategy, synchronization topology, artifact provenance, configuration layers, performance budgets and preservation invariants.

## Difficulty

**Hard: 8 / 8**

The `cuda-async-pipeline-005` entry visible at repository level is a Git submodule and is therefore intentionally excluded from this in-repository domain count.
