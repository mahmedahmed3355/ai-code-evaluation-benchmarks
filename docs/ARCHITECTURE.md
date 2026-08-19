# Architecture

## Overview

This repository is a benchmark portfolio containing reproducible,
Terminal-Bench-style engineering tasks.

The repository is organized around isolated benchmark tasks and a small
Python tooling layer used to validate repository-wide invariants.

## Task Architecture

A benchmark task typically separates the agent environment from the verifier
environment.

Typical task structure:

```text
task/
├── environment/
│   ├── Dockerfile
│   └── data/
├── tests/
│   ├── Dockerfile
│   ├── test.sh
│   └── test_outputs.py
├── solution/
│   └── solve.sh
├── instruction.md
├── README.md
└── task.toml
The environment image contains the files, dependencies, and intentionally
broken state exposed to the benchmark agent.

The tests image contains the verifier dependencies and hidden validation logic.
Solution and verifier assets are kept separate from the agent environment to
reduce solution leakage.

Repository Tooling

The scripts/ package provides repository-level validation and quality checks.

These checks include:

task structure validation
task isolation checks
task manifest validation
validation metrics
structured logging
Docker dependency pinning checks

The dependency checker scans repository Dockerfiles and verifies that base
images are version-pinned and direct pip install package dependencies are
pinned or supplied through requirement or constraint files.

CI Architecture

GitHub Actions runs two independent validation paths.

Tests and Quality Checks

The quality job performs:

dependency lock verification
dependency installation with uv
pytest execution
coverage validation
Ruff linting
MyPy type checking
benchmark task validation
task isolation validation
task manifest validation
dependency auditing with pip-audit
Docker dependency pinning validation
fresh-clone bootstrap and smoke testing
Docker and Kubernetes Validation

The infrastructure validation job performs repository-wide checks for
container and Kubernetes assets.

It includes:

Hadolint analysis for Dockerfiles
Trivy configuration scanning
kubeconform validation for Kubernetes manifests
Kustomize rendering validation for the Kubernetes benchmark task

Kustomization files are rendered with kubectl kustomize instead of being
validated as ordinary Kubernetes resources.

Infrastructure Footprint

The benchmark portfolio contains multiple Docker-based execution environments
across CUDA, GPU, backend, distributed systems, algorithms, Arabic evaluation,
and infrastructure tasks.

Dockerfiles are divided primarily between:

environment/Dockerfile: the isolated environment visible to the agent
tests/Dockerfile: the independent verifier environment

The repository also contains Kubernetes configuration for the
infrastructure/kubernetes-rollout-recovery-010 benchmark task.

These manifests are validated in CI using strict schema validation and
Kustomize rendering.

Reproducibility

Reproducibility is enforced through several layers:

locked Python dependencies with uv.lock
dependency auditing with pip-audit
Docker dependency pinning checks
deterministic repository validation scripts
isolated environment and verifier images
fresh-clone smoke testing in CI

This design keeps benchmark environments reproducible while allowing each task
to define the dependencies required by its own execution and verification
environment.
