# CUDA Memory Coalescing Performance Regression

A production-style configuration-debugging benchmark for AI coding agents.

## Incident

A simulated CUDA kernel-build pipeline has regressed in memory-access efficiency. The workload set is unchanged, but a local configuration layer is overriding the release memory-access strategy.

The agent must diagnose the effective configuration rather than patching the benchmark.

## What makes the task non-trivial

The repository contains several configuration layers with different responsibilities:

```text
build.conf
release.profile
benchmark.conf
local.override
```

The agent must determine:

- which values are performance-critical
- which configuration layer owns the regression
- whether the effective values are consistent with the release contract
- whether the workload budgets still hold
- whether generated artifacts were rebuilt from the repaired configuration

The benchmark also provides build-history evidence and provenance output so the agent can distinguish a configuration regression from a benchmark regression.

## Evaluation

The independent verifier checks:

- preservation of all workload definitions
- configuration-source preservation
- effective configuration
- configuration provenance
- per-workload performance budgets
- aggregate performance budget
- generated artifact consistency
- benchmark result
- regeneration of derived outputs
- preservation of the benchmark and validation implementation
- resistance to hard-coded reports and generated artifacts

## Environment

CPU-only deterministic simulation. No NVIDIA GPU or network access is required.

## Author

Mohamed Ahmed  
engmohamedelshrbeny@gmail.com  
Forge Bench
