# Dependency Policy

## Repository Tooling Dependencies

Repository-level tooling dependencies are managed through:

- `pyproject.toml`
- `uv.lock`

These dependencies are used for:

- validation scripts
- CI checks
- linting
- type checking
- benchmark verification tooling

The lockfile provides deterministic reproduction of the repository tooling environment.

## Task Runtime Dependencies

Benchmark tasks intentionally isolate runtime dependencies.

Each task owns its execution environment through:

- `environment/Dockerfile`
- task-specific configuration files
- task-specific dependency installation steps

Task dependencies are not merged into the repository tooling dependency graph.

This separation prevents dependency conflicts between unrelated benchmark scenarios and preserves reproducibility.

## Dependency Verification

The repository validates dependencies through:

- `uv lock --check`
- `pip-audit` in CI
- Dependabot updates
- task dependency validation scripts

Task isolation is considered part of the benchmark design rather than a missing dependency manifest.
