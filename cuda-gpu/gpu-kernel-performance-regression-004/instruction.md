# GPU Kernel Performance Regression Investigation

You are working in a production-style GPU-kernel build and execution-planning repository.

A recent repository change introduced a performance regression. The generated artifact can still look structurally valid and ordinary correctness checks can pass, but the execution plan violates the performance contract for the supported workloads.

Your task is to investigate the complete pipeline, identify the underlying cause, and repair the repository.

## Objective

Restore the intended release execution behavior without replacing the existing pipeline or weakening its validation.

The final repository must:

- produce a valid execution artifact;
- produce a valid execution plan;
- preserve correctness behavior;
- satisfy every supported workload budget;
- satisfy the aggregate performance budget;
- preserve artifact and plan provenance;
- retain legitimate local diagnostic configuration;
- pass the complete validation workflow.

## Investigation

Start by inspecting `/app`.

Trace the path from configuration sources through:

```text
configuration sources
        ↓
effective configuration
        ↓
execution plan
        ↓
build artifact
        ↓
benchmark
        ↓
validation
```

Use the supplied workload data, diagnostic output, and historical build evidence.

Do not assume that the regression is caused by one numeric threshold.

Pay particular attention to:

- source precedence;
- which settings belong to the release performance contract;
- which local settings are compatibility or diagnostic-only;
- workload profiles;
- per-workload budgets;
- aggregate budget;
- generated plan values;
- artifact provenance;
- stale artifacts;
- correctness versus efficiency.

Reproduce the regression before making the repair.

## Performance contract

The benchmark contract contains both per-workload limits and an aggregate limit.

Every supported workload must remain within its own budget.

The total work must also remain within the aggregate budget.

The release strategy is part of the performance contract.

A correct solution must restore the intended release configuration rather than merely changing the reported score or budget.

## Configuration semantics

The repository contains multiple configuration sources with different responsibilities.

The final configuration must preserve the release performance contract while retaining local settings that are not part of that contract.

Do not delete `local.override` as a shortcut.

Do not discard legitimate diagnostic settings simply because the file also contains legacy performance values.

The correct behavior must remain reproducible from the repository's configuration sources.

## Requirements

Your solution must:

- preserve the existing build and validation pipeline;
- preserve the workload dataset;
- preserve the public script interfaces;
- restore the intended release execution strategy;
- retain allowed local diagnostic configuration;
- regenerate the execution plan;
- regenerate the build artifact;
- keep provenance consistent;
- pass correctness and performance validation.

## Constraints

Do not:

- modify the test suite;
- modify verifier behavior;
- delete or rename configuration sources;
- delete or change workload rows;
- increase any performance budget;
- lower any benchmark requirement;
- fake measured work;
- hard-code expected workload results;
- bypass the benchmark;
- generate a fake artifact;
- replace the pipeline with an unrelated implementation;
- rely on external services or network access.

A solution that makes the validator report success without fixing the effective execution configuration is incomplete.

## Completion criteria

The task is complete only when:

1. the effective configuration satisfies the release contract;
2. all supported workloads satisfy their individual budgets;
3. aggregate work remains within the project budget;
4. the generated artifact matches the generated plan and configuration provenance;
5. the normal validation workflow passes.
