# Security Policy

## Security Model

This repository contains benchmark tasks for evaluating AI coding agents.

Task environments are designed to isolate agents from:

- Hidden verifier logic
- Reference solutions
- Evaluation secrets
- Host credentials
- Production infrastructure

No benchmark task should contain production credentials, API keys, private tokens, or real infrastructure secrets.

## Secret Handling

Secrets must never be committed to the repository.

Where a task requires configuration resembling credentials, use one of:

- Environment variables
- `.env.example` placeholders
- Test-only dummy values
- Kubernetes Secret resources containing non-production values

Real secrets must be supplied externally by the execution environment.

## Verifier Isolation

Reference solutions and hidden evaluation logic must remain outside the agent-visible environment.

Task environment Dockerfiles must not copy:

- `solution/`
- Hidden verifier data
- Private test fixtures

Verification is performed separately from the agent execution environment.

## Infrastructure Security

Infrastructure-oriented assets are validated in CI.

Contributors should avoid:

- Privileged containers
- Hardcoded credentials
- Unnecessary host access
- Production infrastructure configuration

## Reporting Security Issues

If you discover a security issue in repository tooling or task isolation, report it privately with enough information to reproduce the issue.

Do not include real credentials or sensitive data in public issues.
