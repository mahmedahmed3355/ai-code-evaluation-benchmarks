# cuda-memory-pool-007

## Scenario

A memory-intensive CUDA-style pipeline has a production performance regression after a local configuration override changed the allocation lifecycle. The benchmark models allocation, synchronization, reuse, and chunk-management costs across five workload shapes.

This is a configuration-debugging task rather than a CUDA compilation exercise. The agent must reason about configuration precedence, workload characteristics, generated artifacts, and performance budgets.

## Why the regression is realistic

The failure is caused by a coherent set of memory-lifecycle choices: legacy allocation, disabled pooling/reuse, broad synchronization, and an overly small pool chunk. These choices interact strongly with allocation-heavy and reuse-heavy workloads.

The environment is CPU-only and deterministic. It uses a workload dataset plus generated build artifacts to model the performance contract without requiring a GPU.

## Evaluation

The independent verifier checks:

- workload preservation;
- configuration-source preservation;
- effective configuration;
- execution-plan consistency;
- artifact consistency;
- per-workload and aggregate performance budgets;
- benchmark/report consistency;
- negative-baseline behavior;
- generated-output provenance.

The reference solution repairs the local override and runs the normal validation workflow.

## Expected workflow

Investigate → repair the responsible configuration layer → run the supplied validation workflow → leave generated outputs consistent with the final configuration.

## Runtime

- CPU-only
- no network
- deterministic
- Dockerized
- independent verifier
