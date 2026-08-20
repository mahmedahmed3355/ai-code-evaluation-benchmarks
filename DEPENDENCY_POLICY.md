# Dependency Inventory Policy

## Repository Dependencies

The repository uses a separated dependency model.

Repository tooling dependencies are managed through:

- pyproject.toml
- uv.lock

These dependencies include:

- validation tooling
- CI utilities
- linting
- type checking
- benchmark verification scripts


## Benchmark Task Dependencies

Benchmark tasks are intentionally isolated.

Each task owns its runtime environment:

- environment/Dockerfile
- task-specific dependency installation
- task execution requirements

Task dependencies are not merged into the root Python environment.

This prevents conflicts between independent benchmark scenarios.


## Security Validation

Dependencies are verified through:

- uv lock verification
- pip-audit CI checks
- Dependabot updates
- task dependency validation scripts

The repository dependency graph and task dependency graphs are intentionally separated.
