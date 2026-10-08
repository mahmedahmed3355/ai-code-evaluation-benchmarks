# CUDA Memory Coalescing Performance Regression

A simulated CUDA kernel-build pipeline has developed a release performance regression. The application does not contain a broken kernel implementation; the incident is caused by an incorrect effective memory-access configuration.

Investigate the configuration layers, workload definitions, build history, and generated diagnostics. Identify which layer introduced the regression and restore the intended optimized strategy without changing the benchmark or validation machinery.

## Requirements

- Preserve every row in `datasets/workload.csv`.
- Preserve all configuration sources and their roles.
- Fix the regression at the configuration layer that introduced it.
- Preserve configuration provenance.
- Keep the release profile and benchmark contract intact.
- Do not modify benchmark, validation, plan-generation, or artifact-generation logic.
- Do not modify `/tests`.
- Do not hard-code workload names, inputs, work-unit totals, reports, or generated artifacts.
- Do not delete a configuration source to alter precedence.
- Do not disable, weaken, or bypass a performance check.
- Do not replace the memory-access strategy with a different architecture.
- Regenerate all derived outputs after the configuration repair.
- The final configuration must satisfy both the aggregate performance budget and every per-workload budget.
- The generated artifact must describe the actual effective configuration and plan.
- The configuration must retain a traceable source for every effective performance setting.

## Performance model

The plan generator models memory transactions. Poorly coalesced, unaligned, scalar access and the disabled fast path increase work. Block size also affects the amount of work generated for each workload.

The correct repair is a coherent memory-access configuration, not an isolated change to one parameter.

## Acceptance criteria

The complete validation pipeline must pass.

The effective configuration must match the intended release memory-access contract.

All supported workloads must remain present and within their declared budgets.

The artifact, configuration provenance, execution plan, and benchmark report must be internally consistent.

The repair must preserve asynchronous GPU-oriented configuration semantics rather than hiding the regression.
