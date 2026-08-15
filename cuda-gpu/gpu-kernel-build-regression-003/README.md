# GPU Kernel Build Regression 003

## Overview

This task simulates a production-style GPU kernel build regression in which the
repository continues to build successfully, but the generated artifact no
longer satisfies the project's optimization contract.

The failure is intentionally distributed across the configuration resolution,
build, artifact generation, diagnostic, and benchmark workflow.

## Objective

Investigate the repository and restore the intended build behavior without
replacing or bypassing the existing build and validation workflow.

The final implementation must:

- produce a valid build artifact;
- satisfy the required optimization configuration;
- pass the benchmark contract;
- pass the complete validation workflow;
- remain correct when legacy configuration values change.

## Repository Structure

text
gpu-kernel-build-regression-003/
├── environment/
│   ├── Dockerfile
│   └── data/
│       ├── configs/
│       ├── logs/
│       └── scripts/
├── instruction.md
├── solution/
│   └── solve.sh
├── task.toml
├── tests/
│   ├── test_outputs.py
│   └── test.sh
└── README.md

Main Workflow

The repository follows this workflow:

configuration sources
        ↓
configuration resolution
        ↓
effective configuration
        ↓
artifact generation
        ↓
artifact inspection
        ↓
benchmark contract
        ↓
validation result
Validation

The normal validation workflow is:

/app/scripts/validate.sh

The complete verifier can be executed through:

bash /tests/test.sh

The verifier checks repository structure, build behavior, effective
configuration, artifact consistency, benchmark behavior, validation integrity,
legacy configuration handling, invalid artifact rejection, and diagnostic
behavior.

Environment

The task intentionally does not require:

an NVIDIA GPU;
CUDA drivers;
CUDA toolkit installation;
large GPU container images.

The environment is CPU-only and uses a lightweight Python container.

Development Note

The task is designed around investigation and root-cause analysis rather than
simply producing a hardcoded expected output.

Do not modify the test suite or bypass the validation workflow when solving the
task.
