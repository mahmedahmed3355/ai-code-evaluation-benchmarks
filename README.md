# AI Code Evaluation Benchmarks

> A curated portfolio of challenging, reproducible software-engineering tasks
> designed for evaluating AI coding agents, LLM reasoning, debugging, and
> systems-level engineering capabilities.

This repository contains a collection of Terminal-Bench 3–style evaluation
tasks covering CUDA/GPU engineering, backend systems, distributed systems,
infrastructure, algorithms, and multilingual software evaluation.

The benchmark is designed around a simple principle:

**The agent should solve the engineering problem — not discover the test.**

---

## Overview

This project focuses on building realistic software-engineering evaluation
tasks that require an AI coding agent to inspect an environment, reason about
multiple interacting artifacts, identify the underlying failure, and implement
a minimal and coherent repair.

The tasks are intentionally designed to go beyond simple bug fixing.

Many tasks require reasoning across:

- Multiple configuration artifacts
- Runtime state
- Cross-component invariants
- Distributed-system semantics
- Performance constraints
- Concurrency and synchronization
- Recovery behavior
- API contracts
- Workload preservation
- Build and deployment configuration

The goal is to evaluate whether an AI agent can perform engineering work that
resembles real production debugging rather than solving isolated programming
exercises.

---

# Benchmark Domains

The current portfolio contains **20 evaluation tasks** across six domains.

| Domain | Tasks |
|---|---:|
| CUDA / GPU Engineering | 9 |
| Backend Engineering | 3 |
| Distributed Systems / FastAPI | 3 |
| Infrastructure / Kubernetes / Kafka | 2 |
| Algorithms / Optimization | 2 |
| Arabic Language Evaluation | 1 |
| **Total** | **20** |

---

## CUDA / GPU Engineering

The CUDA track focuses on low-level GPU correctness, memory behavior,
synchronization, asynchronous execution, and performance-sensitive failures.

Examples include:

- CUDA memory allocation
- CUDA memory pools
- Memory coalescing
- Shared-memory race conditions
- CUDA streams and events
- Asynchronous pipelines
- Kernel build regressions
- Kernel performance regressions
- GPU memory behavior

These tasks are designed to require reasoning about GPU execution semantics
rather than simply modifying source code until a visible test passes.

---

## Backend Engineering

Backend tasks cover production-style service behavior including:

- Service recovery
- Asynchronous job recovery
- Nginx request logging

The focus is on state consistency, operational correctness, API/service behavior,
and recovery semantics.

---

## Distributed Systems

The distributed-systems track includes FastAPI and concurrency-oriented tasks
covering:

- GPU inference APIs
- Idempotency
- Async concurrency

These tasks evaluate whether an agent can reason about asynchronous execution,
request semantics, concurrency, and cross-component behavior.

---

## Infrastructure

Infrastructure tasks currently include:

- Kubernetes rollout recovery
- Kafka consumer offset recovery

The Kafka task, for example, requires reasoning across consumer identity,
partition ownership, generation/assignment epochs, committed offsets,
processed offsets, checkpoint state, and restart semantics.

The objective is not simply to modify one incorrect value, but to restore a
coherent distributed recovery contract while preserving existing workloads
and committed progress.

---

## Algorithms / Optimization

The algorithmic track includes optimization-focused tasks such as:

- Linear-programming simplex optimization
- Constrained optimization using KKT conditions

These tasks evaluate mathematical reasoning together with implementation
correctness and deterministic verification.

---

## Arabic Evaluation

The repository also includes multilingual evaluation work, including an
Arabic grammatical number-agreement task.

The same benchmark principles are applied to language-oriented tasks:
deterministic correctness, artifact isolation, explicit invariants, and
resistance to shortcut solutions.

---

# Terminal-Bench 3 Architecture

The tasks follow a Terminal-Bench 3–oriented structure.

A typical task contains:

```text
task/
├── environment/
│   ├── Dockerfile
│   └── data/
├── instruction.md
├── README.md
├── task.toml
├── solution/
│   └── solve.sh
└── tests/
    ├── Dockerfile
    ├── test.sh
    └── test_outputs.py
