# Benchmark Portfolio Architecture

## Purpose

This repository is an AI coding agent evaluation benchmark portfolio.

It provides isolated benchmark tasks designed for automated agent evaluation.

Each task contains:

- environment image definition
- hidden verification logic
- reference solution
- deterministic tests


## Execution Model

Tasks execute inside isolated Docker environments.

This repository is not a production cloud service.

Docker and Kubernetes assets exist to reproduce benchmark environments
and validate infrastructure-related engineering scenarios.


## Infrastructure Scope

The repository contains:

- Docker based task environments
- Kubernetes manifests for infrastructure benchmark tasks
- CI validation pipelines

Persistent cloud infrastructure is intentionally not part of this project.


## Validation Pipeline

CI validates:

- Python quality with Ruff and MyPy
- Automated tests
- Dependency security
- Dockerfile quality
- Kubernetes policy compliance
- Task isolation


## Observability

Logging and metrics utilities provide CI-time validation observability.

They support benchmark execution reporting and debugging,
not a production API service.

### Validation Observability Runtime

Validation observability is coordinated through
`scripts/validation_runtime.py`.

The runtime owns a `ValidationMetrics` instance and an `ErrorTracker`
instance. Validation success and failure events update these components
together, preventing metrics and error state from diverging.

`scripts/health.py` and `scripts/validation_report.py` consume the shared
runtime state rather than constructing independent observability snapshots.
This creates a single in-process contract for validation metrics, structured
errors, health reporting, and CI diagnostics.

## Task Build Validation

Repository task validation has two distinct levels.

Structural validation checks that benchmark tasks contain the required task
definition, environment, solution, and verification files. This validation is
used by the normal repository quality workflow.

The optional `make task-build` target performs a deeper local check by building
task environment and verifier images. Some historical or experimental benchmark
tasks may not currently build successfully because they depend on unavailable,
legacy, or task-specific container requirements.

A failed task image build therefore identifies a task environment issue and does
not by itself indicate a repository-wide CI or source-quality regression.
