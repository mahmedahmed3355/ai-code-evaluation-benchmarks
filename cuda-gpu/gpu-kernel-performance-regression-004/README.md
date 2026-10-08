# GPU Kernel Performance Regression 004

## Overview

This benchmark models a production incident in a GPU-kernel build and execution-planning pipeline.

The repository combines layered build configuration, a release performance contract, workload-specific budgets, execution-plan generation, artifact generation, provenance metadata, benchmark validation, diagnostic tooling, and historical build evidence.

A recent configuration change caused a release workload to fall back to a legacy execution strategy. The resulting artifact can still be structurally valid and can preserve numerical correctness, but its work profile violates the performance contract.

The intended repair is not a benchmark bypass. The agent must determine which configuration sources are authoritative, preserve legitimate local diagnostic settings, and restore a reproducible release configuration.

## What makes the task difficult

The failure is distributed across several artifacts rather than exposed as a single broken constant.

The agent must reason about:

1. configuration precedence;
2. protected release settings;
3. local compatibility overrides;
4. workload profiles and per-workload budgets;
5. execution-plan generation;
6. artifact provenance;
7. stale or tampered artifacts;
8. the distinction between correctness and performance;
9. the difference between a validation symptom and the underlying cause.

A superficially successful build is not sufficient.

## Evaluation

The independent verifier checks the resulting repository rather than trusting the benchmark script alone.

It validates:

- effective release configuration;
- preservation of allowed local settings;
- all supported workloads;
- per-workload work budgets;
- aggregate work budget;
- execution-plan contents;
- artifact/config/plan provenance;
- correctness of generated artifacts;
- resistance to stale and tampered artifacts;
- normal validation workflow;
- diagnostic evidence.

## Constraints

The solution must preserve the existing pipeline and data model. It must not:

- delete the legacy configuration source;
- remove supported workload rows;
- weaken performance budgets;
- bypass benchmark execution;
- hard-code expected workload results;
- replace the execution-plan pipeline;
- modify the verifier;
- depend on network access.

## Repository layout

```text
environment/
├── data/
│   ├── configs/
│   ├── datasets/
│   ├── logs/
│   └── scripts/
├── Dockerfile
solution/
└── solve.sh
tests/
├── Dockerfile
├── test.sh
└── test_outputs.py
```

## Expected engineering outcome

A correct repair restores the release execution strategy while keeping non-performance local diagnostics available. The generated plan and artifact must be derived from the repaired configuration, and their provenance must remain internally consistent.

## Author

**Mohamed Ahmed**  
**engmohamedelshrbeny@gmail.com**  
Forge Bench
