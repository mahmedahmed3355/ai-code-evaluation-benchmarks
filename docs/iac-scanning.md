# Infrastructure Policy Scanning

## Scope

Infrastructure assets are validated as part of CI.

Scanned resources include:

- Dockerfiles under benchmark task environments
- Kubernetes manifests under infrastructure tasks

## Tools

The validation pipeline uses:

- Hadolint for Dockerfile linting
- Checkov for Docker and Kubernetes policy checks
- kubeconform for Kubernetes schema validation

## Policy Model

Benchmark infrastructure is intentionally ephemeral.

There is no persistent cloud state or Terraform backend.

Docker and Kubernetes assets exist to provide reproducible
AI agent evaluation environments.

## Accepted Exceptions

Checkov suppressions are documented in `.checkov.yaml`.

Each suppression represents an intentional benchmark design decision.
