.PHONY: validate validate-all test lint typecheck audit check install

install:
	python3 -m pip install -r requirements.lock

validate:
	python3 scripts/validate_tasks.py

validate-all: validate

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check .

typecheck:
	python3 -m mypy scripts tests

audit:
	python3 -m pip_audit -r requirements-dev.txt

check: test lint typecheck audit validate-all
