# CUDA Asynchronous Memory Allocator Regression

You are debugging a deterministic simulation of a production CUDA memory-management configuration. The incident is a regression in allocator semantics: a previously asynchronous, stream-ordered allocation path has been replaced by a synchronous/default path.

Your job is to restore the intended runtime contract **without changing the supported workload definitions or the validation program**.

## Required outcome

The effective configuration must restore all of the following:

- `cudaMallocAsync` allocation and `cudaFreeAsync` release.
- CUDA memory-pool usage.
- Stream-ordered release.
- Deferred release where the workload requires it.
- Cross-stream event synchronization.
- Exactly two execution streams.
- Synchronization before release.
- A positive memory-pool release threshold.
- The existing memory policy and workload definitions.

The four supported workloads are part of the contract. Do not delete, rename, reorder, resize, or move them to make validation easier.

## Investigation guidance

Start by inspecting:

- `/app/data/allocator_config.json`
- `/app/data/workloads.json`
- `/app/data/validate_allocator.py`

Run the validator before and after your repair. The validator is an independent contract check; do not modify it.

The configuration is intentionally degraded at the start. The correct repair is a configuration repair, not a rewrite of the validator or workload data.

## Constraints

Do not:

- modify `/app/data/validate_allocator.py`;
- modify `/app/data/workloads.json`;
- remove validation checks;
- hard-code a PASS result;
- replace the validator with a custom script;
- delete or rename supported workloads;
- bypass the allocator configuration;
- add external dependencies or network access.

Keep the existing repository structure.

A solution is complete only when the original validation program exits successfully.
