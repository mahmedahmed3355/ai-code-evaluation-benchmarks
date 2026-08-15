# GPU Kernel Performance Regression 004

## Overview

This task investigates a performance regression in a GPU-kernel execution
planning and validation pipeline.

The repository contains configuration sources, workload definitions,
execution-plan generation, artifact generation, benchmarking, validation,
and diagnostic tooling.

A recent configuration change causes the effective execution strategy to
violate the intended performance contract while the generated artifact may
still appear valid.

## Objective

Identify and repair the underlying configuration or implementation regression
so that the repository:

- generates a valid execution plan;
- produces a valid build artifact;
- preserves correctness;
- satisfies the intended performance contract;
- remains correct across all supported workloads;
- passes the complete validation workflow.

## Repository Structure

```text
environment/
├── data/
│   ├── configs/
│   ├── datasets/
│   ├── logs/
│   └── scripts/
└── Dockerfile

solution/
└── solve.sh

tests/
├── Dockerfile
├── test.sh
└── test_outputs.py
