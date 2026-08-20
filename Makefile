.PHONY: setup install test lint lint-iac typecheck validate coverage validate-all audit lock-check smoke task-smoke task-build task-manifest

setup:
	uv sync --group dev --locked

install:
	uv sync --group dev --locked

test:
	uv run python -m pytest tests/ -v

lint:
	uv run python -m ruff check .

lint-iac:
	uv run python -m scripts.validate_k8s_security
	command -v kubectl >/dev/null || { echo "kubectl is required for lint-iac"; exit 1; }
	kubectl kustomize infrastructure/kubernetes-rollout-recovery-010/base >/dev/null

typecheck:
	uv run python -m mypy scripts tests

validate:
	uv run python -m scripts.validate_tasks

task-smoke:
	uv run python -m scripts.task_isolation

task-build:
	uv run python -m scripts.task_isolation --build-images

task-manifest:
	uv run python -m scripts.task_manifest

coverage:
	uv run python -m pytest tests/ \
		--cov=scripts.logging_config \
		--cov=scripts.validation_metrics \
		--cov=scripts.validate_tasks \
		--cov=scripts.task_isolation \
		--cov=scripts.task_manifest \
		--cov-report=term-missing \
		--cov-fail-under=70

audit:
	uv run pip-audit

lock-check:
	uv lock --check

validate-all: lock-check lint typecheck test validate coverage

smoke:
	uv sync --group dev --locked
	$(MAKE) validate-all
	$(MAKE) task-smoke
	$(MAKE) task-manifest


validate-task:
	@if [ -z "$(TASK)" ]; then 		echo "Usage: make validate-task TASK=<task-path>"; 		exit 1; 	fi
	uv run python -m scripts.task_isolation --task $(TASK)


smoke-task:
	@if [ -z "$(TASK)" ]; then \
		echo "Usage: make smoke-task TASK=<task-path>"; \
		exit 1; \
	fi
	uv run python -m scripts.task_smoke --task $(TASK)


dependency-report:
	uv run python -m scripts.generate_dependency_inventory
