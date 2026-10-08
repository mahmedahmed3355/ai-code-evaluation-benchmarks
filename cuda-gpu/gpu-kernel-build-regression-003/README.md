# GPU Kernel Build Regression 003

## Overview

This benchmark models a production build-pipeline incident in which a GPU-kernel release artifact is generated successfully but is built from the wrong configuration. The repository also contains an artifact-integrity weakness: the benchmark can trust values embedded in an artifact without proving that the artifact belongs to the configuration currently being validated.

The challenge is to recover the intended build semantics rather than patching one observed value.

## Engineering scenario

The pipeline has four configuration layers:

- `build.conf` — base build configuration;
- `release.profile` — authoritative release optimization profile;
- `benchmark.conf` — workload and validation requirements;
- `local.override` — legacy compatibility settings.

The regression occurs because these layers are resolved with the wrong precedence. The validation path has a separate trust boundary around the generated artifact.

## Workflow

```text
configuration sources
        |
        v
configuration resolution
        |
        v
effective configuration
        |
        v
artifact generation + provenance
        |
        v
artifact inspection
        |
        v
benchmark integrity + optimization checks
        |
        v
validation result
```

## What makes it difficult

A superficial repair can make the first artifact look correct while leaving the system vulnerable to:

- legacy overrides replacing release settings;
- unrelated local settings being discarded;
- stale artifacts surviving configuration changes;
- artifact fields being edited without matching provenance;
- benchmark success being inferred from self-reported artifact values.

The verifier therefore exercises both normal operation and adversarial configuration/artifact states.

## Environment

The task is CPU-only and does not require CUDA drivers or an NVIDIA GPU. The repository represents a GPU-kernel build pipeline at the configuration and artifact-validation layer.

Internet access is not required.

## Expected engineering behavior

A correct solution should preserve the existing scripts and interfaces while establishing:

1. deterministic configuration precedence;
2. protection of release optimization fields;
3. preservation of legitimate non-contract local settings;
4. artifact/configuration provenance;
5. rejection of stale or tampered artifacts;
6. a passing end-to-end validation workflow.

## Verification

The verifier checks repository integrity, configuration precedence, build output, artifact provenance, benchmark behavior, stale-artifact rejection, local-setting preservation, and complete validation.

Do not modify the verifier to make the task pass.
