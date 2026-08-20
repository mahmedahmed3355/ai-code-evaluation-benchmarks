# Infrastructure Policy Scanning

## Scope

Infrastructure assets are validated as part of CI.

Scanned resources include:

- Dockerfiles under benchmark task environments
- Kubernetes manifests under infrastructure tasks
- Terraform infrastructure modules under infra

## Tools

The validation pipeline uses:

- Hadolint for Dockerfile linting
- Checkov for Docker, Kubernetes, and Terraform policy checks
- kubeconform for Kubernetes schema validation
- Terraform formatting, validation, and planning for Terraform modules

## Terraform Model

The repository contains reusable Terraform modules for optional benchmark infrastructure provisioning.

Terraform modules support isolated benchmark execution environments without committing deployment credentials or persistent state.

CI initializes Terraform with backend disabled and then runs validation and planning.

No Terraform state files are committed to the repository.

Consumers performing real deployments must configure an appropriate remote state backend and locking strategy for their environment.

## Policy Model

Benchmark infrastructure is intentionally reproducible and isolated.

Docker and Kubernetes assets provide task execution environments, while Terraform modules provide optional reusable provisioning primitives.

## Accepted Exceptions

Checkov suppressions are documented in .checkov.yaml.

Each suppression represents an intentional benchmark design decision.
