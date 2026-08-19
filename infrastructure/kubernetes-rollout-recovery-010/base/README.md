# Kubernetes Base Module

This directory contains a reusable Kubernetes base for the
`kubernetes-rollout-recovery-010` benchmark task.

The benchmark environment keeps the task-specific manifest under
`environment/data/`. This base module provides a separately structured
Kubernetes configuration that can be validated independently.

## Validate

From the `base/` directory:

    kubeconform -strict -summary deployment.yaml

## Render

From the `base/` directory:

    kubectl kustomize .

## Build

From `infrastructure/kubernetes-rollout-recovery-010`:

    kubectl kustomize base
