# Benchmark Infrastructure

This directory contains reusable infrastructure definitions for isolated benchmark execution environments.

The benchmark portfolio primarily uses Docker and Kubernetes task environments.
Terraform provides an optional provisioning layer for deployments that need reusable Kubernetes namespaces before benchmark execution.

## Module

The benchmark-namespace module creates a Kubernetes namespace intended for isolated benchmark execution.

The module uses a pinned Kubernetes provider version, applies benchmark ownership and isolation labels, enables restricted Pod Security Admission labels, accepts additional caller-defined labels, and does not create credentials or secrets.

## Validation

Terraform infrastructure is validated in CI with formatting, initialization without a backend, validation, planning, and Checkov policy scanning.

CI uses terraform init with backend disabled because this repository provides reusable infrastructure modules rather than managing production deployment state.

No Terraform state files are committed to the repository.

Consumers deploying these modules in real environments are responsible for configuring an appropriate remote backend and state locking mechanism.

## Local Example

The local example demonstrates module usage from infra/examples/local.

A configured Kubernetes provider is required when applying the example.
