# GPU Kernel Performance Regression Investigation

You are working in a small production-style kernel planning and validation
repository.

A recent repository change introduced a performance regression in the
execution plan used to process a large workload. The generated artifact still
produces correct results, and the ordinary correctness checks may pass, but
the resulting execution plan violates the project's performance contract.

Your task is to investigate the repository, identify the root cause of the
performance regression, and repair the project so that both correctness and
efficiency requirements are satisfied.

## Objective

Restore the intended execution strategy without replacing the existing
pipeline or bypassing its validation.

The final repository must:

- produce a valid execution artifact;
- produce correct results;
- satisfy the project's performance/work budget;
- pass the complete validation workflow;
- remain correct for the supported workload sizes;
- preserve the existing project structure and workflow.

Correctness alone is not sufficient for task completion.

## Investigation

Start by inspecting the repository under `/app`.

Use the available scripts, configuration files, datasets, generated artifacts,
diagnostic output, and logs to understand the complete execution path.

Do not assume that the observed performance regression is caused by a single
constant or threshold.

Investigate:

- input-size handling;
- execution-plan generation;
- algorithm/strategy selection;
- configuration precedence;
- work-unit calculation;
- generated artifact metadata;
- correctness validation;
- performance measurement;
- benchmark thresholds;
- and relevant historical or diagnostic logs.

Reproduce the observed behavior before deciding on a fix.

A successful correctness check does not establish that the implementation is
correct for this task.

## Performance Contract

The repository contains a performance/work contract that applies to the
supported workloads.

The implementation must satisfy the contract without simply weakening its
requirements.

The measured work must remain within the project's intended budget for the
provided workloads.

Solutions that merely increase the allowed budget, lower the required score,
or bypass the performance measurement are incomplete.

## Requirements

Your solution must:

- preserve the existing execution pipeline;
- preserve the existing interfaces;
- preserve the intended correctness behavior;
- preserve supported workload configurations;
- produce an efficient execution plan;
- satisfy both correctness and performance validation.

The solution must address the underlying cause of the regression.

## Constraints

Do not:

- replace the existing pipeline with a different implementation;
- remove or disable correctness checks;
- remove or disable performance checks;
- modify the test suite;
- modify reference data;
- hardcode expected benchmark results;
- increase performance budgets to hide the regression;
- lower benchmark requirements;
- fake measured work;
- skip the benchmark stage;
- generate a fake artifact;
- delete unrelated repository files.

Do not solve the task by making the validator report success regardless of the
actual execution plan.

## Validation

After making the fix, run the repository's normal validation workflow.

You should verify both:

1. correctness of the generated result;
2. efficiency of the generated execution plan.

The complete validation workflow must pass.

A solution that only passes correctness checks while violating the performance
contract is incomplete.

A solution that passes one workload but fails another supported workload is also
incomplete.

The task is complete only when the complete validation workflow passes and the
generated artifact satisfies the intended correctness and performance
contracts.
