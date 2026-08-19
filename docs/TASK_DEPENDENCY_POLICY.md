# Task Dependency Policy

Benchmark tasks are intentionally isolated.

Each task owns its execution environment through:

- environment/Dockerfile
- tests/Dockerfile
- task-local dependency installation

The repository root validation tooling is managed through:

- pyproject.toml
- uv.lock

## Dependency Rules

- Task runtime dependencies remain isolated inside each benchmark environment.
- Repository validation dependencies are pinned through uv.lock.
- Docker environments should avoid unpinned package installation when reproducibility is required.
- Task isolation prevents dependency conflicts between benchmark scenarios.

This model keeps benchmark execution deterministic while allowing each
evaluation task to represent a realistic engineering environment.
