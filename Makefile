.PHONY: validate test lint check

validate:
	python3 scripts/validate_tasks.py

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check scripts tests

check: validate test lint
