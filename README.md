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

The current portfolio contains **18 evaluation tasks** across six domains.

| Domain | Tasks |
|---|---:|
| CUDA / GPU Engineering | 9 |
| Backend Engineering | 3 |
| Distributed Systems / FastAPI | 3 |
| Infrastructure / Kubernetes / Kafka | 2 |
| Algorithms / Optimization | 2 |
| Arabic Language Evaluation | 1 |
| **Total** | **19** |

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
The separation between the execution environment and the verifier is a core
part of the benchmark design.

Verifier Isolation

One of the most important design decisions in this repository is the
separation between the agent environment and the verification environment.

Agent Environment

environment/Dockerfile builds the environment available to the coding agent.

It contains the necessary:

Dependencies
Source files
Configuration
Workloads
Input artifacts

The agent environment does not receive the verifier implementation or
reference solution.

For example:

environment/
├── Dockerfile
└── data/

The Docker build explicitly copies only the intended environment data.

Verifier Environment

The verifier has its own Dockerfile:

tests/Dockerfile

This image contains:

Pytest
Verification code
Test infrastructure
Verifier-specific dependencies

The verifier environment is built independently from the agent environment.

This prevents the agent from simply inspecting the evaluator implementation
inside its working environment.

Reference Solutions

Each task contains a reference solution under:

solution/solve.sh

The reference solution is used to establish the intended repaired state and
validate that the task is solvable.

Reference solutions are kept outside the agent's environment.

They are part of the benchmark repository and evaluation development workflow,
not part of the runtime environment presented to the agent.

Deterministic Verification

The benchmark uses deterministic automated verification rather than subjective
evaluation.

Typical verification checks include:

Configuration invariants
State consistency
API contracts
Resource ownership
Offset correctness
Synchronization requirements
Workload preservation
Message accounting
Recovery semantics
Build correctness
Performance-related constraints

Where possible, tests validate the resulting system state rather than checking
whether the agent used a particular implementation.

This allows multiple valid solutions while still enforcing the engineering
contract.

Cross-Artifact Reasoning

A major characteristic of these tasks is cross-artifact reasoning.

Instead of placing the entire bug in one file, related inconsistencies can be
distributed across several artifacts.

For example:

configuration
      │
      ├── generation
      ├── assignment
      └── recovery policy
             │
             ▼
       recovery state
             │
             ├── checkpoints
             ├── committed offsets
             ├── processed offsets
             └── restart state
             │
             ▼
          workloads

The agent must determine which values represent durable truth and which values
represent inconsistent runtime state.

This makes the task substantially harder than a simple single-file repair.

Anti-Leakage Design

The benchmark follows several principles intended to prevent shortcut-based
solutions.

1. Environment / Verifier Separation

Verifier files are not copied into the agent environment.

2. Reference Solution Separation

solution/ is kept outside the agent-visible environment.

3. Artifact Isolation

Only intended task data is copied into the environment image.

4. Canary Tracking

Tasks contain a Harbor canary identifier to help detect accidental artifact
mixing and task contamination during benchmark development.

5. Contract-Based Verification

Tests focus on behavioral and structural invariants instead of exposing a
single expected patch.

6. Preservation Constraints

Many tasks explicitly require preserving unrelated state such as:

Existing workloads
Message counts
Partition topology
API contracts
Resource ownership
Existing configuration

This prevents trivial destructive solutions.

7. Shortcut Rejection

Tasks can explicitly reject approaches such as:

Resetting state destructively
Removing workloads
Disabling the relevant subsystem
Bypassing recovery logic
Replacing the intended mechanism with a global synchronization shortcut
Difficulty Engineering

Task difficulty is treated as an engineering variable rather than simply
adding more lines of code.

Difficulty can come from:

Multiple interacting artifacts
Ambiguous local symptoms
Cross-artifact inconsistencies
Distributed-state reasoning
Concurrency semantics
Hidden dependency relationships
Preservation requirements
Multiple plausible but incorrect repairs
Anti-shortcut constraints
Deterministic but non-obvious invariants

The goal is to create tasks where an agent must understand the system before
performing the repair.

Validation Workflow

Tasks are validated through a repeatable development workflow:

Task Design
    ↓
Environment Construction
    ↓
Reference Solution
    ↓
Deterministic Verifier
    ↓
Local Docker Validation
    ↓
Oracle Validation
    ↓
NOP / Baseline Validation
    ↓
Leakage Audit
    ↓
Harbor Evaluation

A task is not considered ready simply because the reference solution passes.

We also verify that:

The original broken state fails.
The reference solution repairs the state.
The verifier passes after repair.
The agent environment does not contain verifier/reference artifacts.
A no-op agent does not receive credit for the broken state.
The final task remains deterministic and reproducible.
Example: Kafka Consumer Recovery

One representative task models a Kafka consumer recovery regression.

The initial state contains several individually plausible values that become
inconsistent when considered together.

The agent must reconcile:

Consumer identity
       ↓
Partition assignment
       ↓
Generation / assignment epoch
       ↓
Committed offsets
       ↓
Processed offsets
       ↓
Checkpoint state
       ↓
Restart recovery policy

The correct repair must preserve committed progress and resume from durable
state without using destructive offset-reset shortcuts.

This illustrates the benchmark philosophy:

The challenge is understanding the system state, not guessing the expected
file edit.

Example: CUDA Stream/Event Dependency

The CUDA stream/event task models asynchronous execution across multiple CUDA
streams.

The task requires reasoning about:

Producer Stream
      │
      │ producer_done
      ▼
Consumer Stream
      │
      │ consumer_done
      ▼
Finalizer Stream

The repaired configuration must preserve asynchronous execution while
establishing the required cross-stream event dependencies.

A global synchronization shortcut is explicitly rejected.

This evaluates whether an agent understands CUDA stream/event dependency
semantics rather than simply inserting a global synchronization primitive.

Reproducibility

Tasks are packaged as Dockerized environments so that the same benchmark
artifacts can be evaluated consistently.

The benchmark separates:

Agent Environment
        │
        └── environment/Dockerfile


Verifier Environment
        │
        └── tests/Dockerfile

This separation improves reproducibility and makes the evaluation pipeline
portable across machines and benchmark runners.

Repository Structure
ai-code-evaluation-benchmarks/
│
├── cuda-gpu/
│   ├── cuda-memory-allocator-008/
│   ├── cuda-shared-memory-001/
│   ├── cuda-async-pipeline-005/
│   ├── cuda-memory-coalescing-006/
│   ├── cuda-memory-pool-007/
│   ├── cuda-reduction-race-002/
│   ├── cuda-stream-event-dependency/
│   ├── gpu-kernel-build-regression-003/
│   └── gpu-kernel-performance-regression-004/
│
├── backend/
│   ├── backend-service-recovery/
│   ├── backend-async-job-recovery/
│   └── nginx-request-logging/
│
├── distributed-systems/
│   ├── fastapi-idempotency-011/
│   └── fastapi-async-concurrency-009/
│
├── infrastructure/
│   ├── kubernetes-rollout-recovery-010/
│   └── kafka-consumer-offset-recovery/
│
├── algorithms/
│   ├── ml-lp-simplex-optimizer/
│
└── arabic-evaluation/
    └── arabic-count-notification/
Technology

The benchmark currently uses technologies and concepts including:

Terminal-Bench 3
Docker
Python
Pytest
FastAPI
Kafka
Kubernetes
CUDA
GPU memory management
CUDA streams and events
Shared memory
Distributed systems
Backend infrastructure
Optimization algorithms
Arabic language evaluation
Engineering Philosophy

The benchmark is built around five principles:

Correctness over superficial success

A solution should satisfy the underlying engineering contract.

Reproducibility over environment-specific behavior

Tasks should run consistently in isolated environments.

Reasoning over pattern matching

The agent should understand relationships between artifacts.

Verification over trust

Every successful repair should be independently verified.

Real engineering constraints over toy problems

Tasks should resemble the kinds of failures engineers encounter in production
systems: recovery bugs, concurrency errors, state inconsistencies, API
contract violations, infrastructure regressions, and performance problems.

Status

19 tasks currently included.

The repository is being developed as a growing benchmark portfolio for
AI coding-agent evaluation and software-engineering reasoning.

Future work includes expanding the benchmark across CUDA/GPU systems,
distributed training, backend infrastructure, Kubernetes, and additional
multilingual evaluation tasks.

About

Built as an independent software-engineering evaluation benchmark portfolio
using Terminal-Bench 3–oriented task architecture, Dockerized environments,
deterministic verification, reference solutions, and anti-leakage principles.

---

# Reproduce Locally

The repository can be validated from a fresh clone with the following workflow.

## 1. Clone the repository

```bash
git clone https://github.com/mahmedahmed3355/ai-code-evaluation-benchmarks.git
cd ai-code-evaluation-benchmarks
2. Create a Python environment
python3 -m venv .venv
source .venv/bin/activate
3. Install reproducible development dependencies
make install

The repository uses requirements.lock to provide a reproducible dependency set.

4. Run the complete repository quality suite
make check

This command runs:

Repository tests
Ruff linting across the repository
Static type checking
Dependency vulnerability auditing
Structural validation of all benchmark tasks
5. Validate benchmark task structure
make validate-all

This verifies that every benchmark task contains the required instruction,
environment, reference solution, verifier, and task metadata.
