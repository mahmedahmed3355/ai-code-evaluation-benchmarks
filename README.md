# AI Code Evaluation Benchmarks

> A portfolio of production-style, reproducible benchmark tasks for evaluating AI coding agents on debugging, reasoning, systems engineering, and software correctness.

This repository is built around one principle:

**The agent should solve the engineering problem — not discover the test.**

The benchmark emphasizes realistic failures, cross-artifact reasoning, deterministic verification, isolated Docker environments, preservation constraints, and resistance to shortcut solutions.

## Benchmark at a glance

The current repository contains **33 benchmark task entries in the normal task inventory**, organized across **11 benchmark domains**.

| Domain | Tasks |
|---|---:|
| CUDA / GPU Engineering | 8 |
| Backend Engineering | 4 |
| Distributed Systems | 4 |
| Infrastructure | 4 |
| Machine Learning | 4 |
| Data Engineering & Streaming | 2 |
| MLOps | 2 |
| Security | 2 |
| Kubernetes & Cloud Systems | 1 |
| Algorithms & Optimization | 1 |
| Arabic / Internationalization Evaluation | 1 |
| **Total** | **33** |

> **Repository audit note:** The directory scan currently shows 33 normal task directories in the benchmark inventory. One CUDA entry, `cuda-gpu/cuda-async-pipeline-005`, is a Git submodule rather than a normal task directory, so it is not counted as an in-repository task asset. The table above counts the normal task directories only and should be treated as the canonical benchmark inventory.

## Difficulty distribution

The portfolio is intentionally weighted toward hard systems problems.

| Difficulty | Tasks |
|---|---:|
| Hard | 29 |
| Medium | 3 |
| Easy | 1 |
| **Total** | **33** |

Difficulty is assigned from explicit task metadata where available. Tasks without a formal difficulty field are classified conservatively from their actual scope, test design, and system-level complexity.

## Domains

### CUDA / GPU Engineering — 8 tasks

Low-level GPU correctness, memory management, synchronization, build reproducibility, and performance regression diagnosis.

- `cuda-memory-allocator-008` — **Hard** — asynchronous CUDA allocator semantics, stream ordering, memory-pool reuse and release guarantees.
- `cuda-memory-coalescing-006` — **Hard** — layered configuration debugging, memory-access performance regression, provenance and benchmark consistency.
- `cuda-memory-pool-007` — **Hard** — stream-ordered memory pools, reuse, synchronization and generated-artifact consistency.
- `cuda-reduction-race-002` — **Hard** — multi-stage reduction correctness, empty-input handling and complete partial-sum coverage.
- `cuda-shared-memory-001` — **Hard** — shared-memory synchronization, distributed reduction and barrier ordering.
- `cuda-stream-event-dependency` — **Hard** — CUDA stream/event happens-before edges and asynchronous dependency reconstruction.
- `gpu-kernel-build-regression-003` — **Hard** — build configuration precedence, artifact trust and provenance validation.
- `gpu-kernel-performance-regression-004` — **Hard** — release performance contracts, layered configuration and workload-specific budgets.

### Backend Engineering — 4 tasks

Production service behavior, asynchronous job execution, deployment recovery, reverse proxies and operational correctness.

- `backend-async-job-recovery` — **Hard** — durable job claiming, lease recovery and idempotent effects.
- `backend-production-recovery` — **Hard** — systemd/Gunicorn/Uvicorn/Nginx deployment recovery.
- `backend-service-recovery` — **Hard** — Unix-socket service recovery, proxying and restart resilience.
- `nginx-request-logging` — **Medium** — Nginx configuration, structured request logging, rate limiting and custom error handling.

### Distributed Systems — 4 tasks

Concurrency, distributed training, checkpointing and idempotency under failure.

- `distributed-ddp-accumulation-010` — **Hard** — sample-weighted gradient accumulation, uneven-rank synchronization and deterministic resume.
- `distributed-sharded-checkpoint-012` — **Hard** — atomic sharded checkpoint publication and recovery.
- `fastapi-async-concurrency-009` — **Medium** — eliminating event-loop blocking while preserving API behavior.
- `fastapi-idempotency-011` — **Hard** — race-free idempotency under concurrent requests.

### Infrastructure — 4 tasks

Operational recovery across systemd, Kafka, Kubernetes manifests and durable runtime state.

- `infra-systemd-timer-recovery` — **Hard** — locking, crash recovery, failure propagation and persistent scheduling.
- `kafka-consumer-offset-recovery` — **Hard** — committed-vs-processed offsets, generation/epoch consistency and restart recovery.
- `kubernetes-rollout-recovery` — **Hard** — Deployment/Service/PDB identity and selector reconciliation.
- `systemd-service-recovery` — **Hard** — startup ordering, readiness, restart policy, security and resource contracts.

### Machine Learning — 4 tasks

Inference correctness, model promotion, temporal evaluation and feature-serving contracts.

- `feature-consistent-inference-hardening` — **Hard** — CSV semantics, preprocessing/calibration persistence, artifact consistency and auditability.
- `ml-feature-serving-contract` — **Hard** — persisted feature order, preprocessing, calibration and immutable artifacts.
- `ml-model-promotion` — **Hard** — group-safe splits, train-only preprocessing, validation-only model selection and frozen holdout auditing.
- `ml-temporal-evaluation` — **Hard** — temporal evaluation and leakage-resistant model assessment.

### Data Engineering & Streaming — 2 tasks

- `data-stream-window-recovery-018` — **Hard** — event-time windows, watermarks, late data, deduplication and checkpoint ordering.
- `data-cdc-sink-recovery-019` — **Hard** — partition offsets, at-least-once replay, idempotence, schema evolution and checkpoint recovery.

### MLOps — 2 tasks

- `mlops-model-promotion-gate` — **Hard** — artifact integrity, lineage, freshness, metrics, safety gates and stage transitions.
- `mlops-pipeline-recovery` — **Hard** — DAG recovery, durable event journals, retries, artifact integrity and deterministic replay.

### Security — 2 tasks

- `security-container-hardening` — **Hard** — non-root containers, deterministic images, secrets hygiene and runtime hardening.
- `security-secret-supply-chain-scanner` — **Hard** — secret detection, SARIF generation, ignore semantics and adversarial false-positive resistance.

### Kubernetes & Cloud Systems — 1 task

- `k8s-cloud-rollout-reconciler-020` — **Hard** — rollout planning under readiness, PDB, topology, resource and rollback constraints.

### Algorithms & Optimization — 1 task

- `ml-lp-simplex-optimizer` — **Hard** — constrained linear programming, active-constraint reporting and KKT residuals.

### Arabic / Internationalization Evaluation — 1 task

- `arabic-count-notification` — **Medium** — Arabic grammatical number agreement across count categories.

## Task architecture

A typical benchmark task separates the candidate environment from the verifier and the reference solution:

```text
task/
├── environment/
│   └── Dockerfile
├── instruction.md
├── task.toml
├── solution/
│   └── solve.sh
└── tests/
    ├── Dockerfile
    ├── test.sh
    ├── test_outputs.py
    └── hidden_tests.py
```

The exact files vary by task, but the design goal is consistent:

- isolated candidate environment
- independent verification environment
- reference repair outside the candidate image
- deterministic checks
- hidden/adversarial cases
- preservation constraints
- anti-shortcut validation

## Evaluation philosophy

These tasks are deliberately more demanding than isolated coding exercises. A successful agent often needs to:

1. inspect several interacting artifacts;
2. identify the durable or authoritative source of truth;
3. reason about failure and recovery semantics;
4. preserve unrelated workloads and contracts;
5. implement the smallest coherent repair;
6. survive hidden and adversarial test cases.

Typical invariants include concurrency safety, API compatibility, artifact integrity, configuration precedence, resource ownership, state transitions, workload preservation, synchronization ordering and deterministic recovery.

## Repository-level quality

The repository also contains shared validation and documentation for task structure, dependency management, isolation, CI, security checks and reproducibility.

See:

- `BENCHMARK_HANDBOOK.md`
- `docs/ARCHITECTURE.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

## Scope note

The benchmark inventory is based on repository contents on the `main` branch and specifically counts normal task directories containing benchmark `task.toml` files. Non-task support directories and Git submodules are not counted as benchmark tasks.

---

## About Forge Bench

Forge Bench is an independent benchmark portfolio focused on realistic AI coding-agent evaluation. The goal is to measure whether an agent can reason about software systems under realistic constraints — not merely satisfy shallow unit tests.

Built by **Mohamed Ahmed**.
