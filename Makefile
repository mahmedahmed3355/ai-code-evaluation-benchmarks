.PHONY: install validate validate-all test lint typecheck audit \
	check test-local verify lock lock-check container-check

install:
	python3 -m pip install -r requirements.lock

validate:
	python3 -m scripts.validate_tasks

validate-all: validate

test:
	python3 -m pytest tests/ -v

coverage:
	python3 -m pytest tests/ --cov=scripts --cov-report=term-missing

lint:
	python3 -m ruff check .

typecheck:
	python3 -m mypy scripts tests

audit:
	python3 -m pip_audit -r requirements-dev.txt

test-local: test lint typecheck audit

check: test-local validate-all

verify: check

lock:
	python3 -m piptools compile \
		--generate-hashes \
		--output-file=requirements.lock \
		requirements.in

lock-check:
	python3 scripts/check_lockfile.py

container-check:
	docker compose up --build --abort-on-container-exit --exit-code-from validator
