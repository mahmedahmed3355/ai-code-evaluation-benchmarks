.PHONY: install test lint typecheck validate coverage validate-all audit lock-check

install:
	uv sync --extra dev --locked

test:
	uv run python -m pytest tests/ -v

lint:
	uv run python -m ruff check .

typecheck:
	uv run python -m mypy scripts tests

validate:
	uv run python -m scripts.validate_tasks

coverage:
	uv run python -m pytest tests/ \
		--cov=scripts.logging_config \
		--cov=scripts.validation_metrics \
		--cov=scripts.validate_tasks \
		--cov-report=term-missing \
		--cov-fail-under=70

audit:
	uv run pip-audit

lock-check:
	uv lock --check

validate-all: lock-check lint typecheck test validate coverage
