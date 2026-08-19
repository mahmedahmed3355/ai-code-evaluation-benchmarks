# Benchmark Dependency Model

## Overview

This repository follows a task-isolated dependency model.

The root repository does not provide runtime dependencies for benchmark tasks.
Each benchmark task owns its own execution environment.

## Dependency Layers

### 1. Repository Development Dependencies

Root-level dependencies are only used for:

- CI validation
- Testing
- Static analysis
- Security auditing

Examples:

- pytest
- pytest-cov
- ruff
- mypy
- pip-audit

### 2. Task Environment Dependencies

Each benchmark task defines its own runtime dependencies inside:

- environment/Dockerfile
- environment/data/requirements.txt

These dependencies are isolated from other tasks.

### 3. Verifier Dependencies

Verifier dependencies are isolated under:

- tests/Dockerfile

They contain only the packages required to execute task validation.

## Dependency Requirements

All task dependencies should:

- use pinned versions where possible
- avoid floating latest versions
- be reproducible from a fresh clone
- remain isolated inside task environments

## Design Rationale

Task isolation prevents dependency conflicts between unrelated benchmark tasks and allows each task to reproduce its intended execution environment independently.
