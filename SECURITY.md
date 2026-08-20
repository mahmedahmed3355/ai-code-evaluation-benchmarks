# Security Policy

## Secret Management

This repository does not store credentials, API keys, or production secrets.

Benchmark tasks must provide secrets through runtime configuration only.
Secrets must never be committed into task environments, Docker images, or
validation artifacts.

For Kubernetes-based tasks, secrets should be provided through Kubernetes
Secrets or equivalent external secret mechanisms.

## Threat Model

The benchmark architecture separates:

- agent execution environments
- verifier environments
- reference solutions
- hidden evaluation data

Agents should only access the files and resources explicitly provided by
the task environment.

Verifier logic, hidden tests, and reference solutions must remain isolated
from agent-visible environments.

## Reporting Issues

Security-related issues should be reported privately through the repository
maintainer contact channel before public disclosure.
