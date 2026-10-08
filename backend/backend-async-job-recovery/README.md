# Durable Async Job Recovery

**Forge Bench — Backend Reliability Evaluation Task**

A production-style debugging task for coding agents. The service is a small
SQLite-backed asynchronous job system whose correctness depends on durable
state transitions rather than in-memory coordination.

## What the agent must repair

The starting implementation contains interacting reliability failures involving:

- concurrent worker claiming;
- durable `pending -> processing` transitions;
- lease-based recovery after worker failure;
- retry behavior after a crash window;
- idempotent logical side effects;
- persistence across worker/module restarts.

The challenge is intentionally cross-component: the correct repair requires
reasoning about the database layer, queue/claim logic, worker lifecycle, and
failure windows together.

## Runtime contract

The public API remains unchanged:

```text
GET  /health
POST /jobs
GET  /jobs/{job_id}
GET  /jobs/{job_id}/effects
```

Jobs are stored in SQLite. Workers discover runnable jobs from durable state.
No external service or GPU is required.

## Evaluation focus

The independent verifier exercises behavior rather than requiring a specific
implementation. It checks normal completion, concurrent claiming, expired
lease recovery, crash-after-effect recovery, persistence, and the invariant
that one completed job has one logical persisted effect.

The environment is CPU-only and network-free. The verifier is isolated from
the agent environment.

## Difficulty design

This task is difficult because several plausible partial fixes are incorrect.
For example, a process-local lock does not provide correctness across worker
processes; simply retrying an effect can create duplicates; and recovering a
lease without an atomic state transition can race with another worker.

The task therefore tests system-level debugging and failure-mode reasoning,
not implementation of a single isolated function.

## Author

**Mohamed Ahmed**  
Senior AI/ML Engineer & Benchmark Engineer  
`engmohamedelshrbeny@gmail.com`

## Forge Bench

This task is part of Forge Bench, a collection of realistic, reproducible,
independently verified evaluation tasks for AI coding agents.
