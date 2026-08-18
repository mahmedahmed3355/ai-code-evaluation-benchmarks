# Contributing

## Development setup

Clone the repository and create a virtual environment:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements-dev.txt

## Validation

Run all repository checks:

    make check

Individual checks are also available:

    make validate
    make test
    make lint

## Adding or modifying a benchmark task

Each task should preserve the repository task structure and include:

- `task.toml`
- `instruction.md` or `instruction_en.md`
- `solution/`
- `tests/`
- `environment/`

Run validation before committing changes:

    make check

Keep commits focused. Changes to a task should include the relevant tests whenever possible.
