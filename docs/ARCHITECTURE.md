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
