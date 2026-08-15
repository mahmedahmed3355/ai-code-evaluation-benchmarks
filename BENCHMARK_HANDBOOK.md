Anti-Cheating & Leakage Resistance

The benchmark uses a defense-in-depth approach rather than relying on a
single anti-cheating mechanism.

1. Environment / Verifier Separation

Verifier files are kept outside the agent-visible environment.

2. Reference Solution Isolation

Reference implementations are not copied into the agent environment.

3. Evaluation Artifact Isolation

The environment image contains only intended task artifacts.

4. Test Leakage Resistance

Evaluation-specific implementation details are not intentionally exposed to
the agent.

5. Expected-Output Protection

Tasks avoid providing a direct expected patch or solution state as part of the
agent-visible specification.

6. Hardcoding Resistance

Verification can include multiple interacting invariants so that hardcoding a
single visible example is insufficient.

7. State-Exploitation Resistance

Tasks can require preservation of unrelated state, workloads, configuration,
ownership, or historical progress.

8. Shortcut Rejection

Verification can explicitly reject destructive or shortcut-based approaches
such as:

Removing workloads
Resetting state destructively
Disabling the relevant subsystem
Bypassing recovery mechanisms
Replacing asynchronous behavior with an invalid global synchronization
Altering unrelated system contracts

The goal is to make the shortest successful path the correct engineering
solution, rather than a benchmark exploit.

Difficulty Engineering

Difficulty is treated as an engineering variable rather than simply adding
more bugs.

The benchmark uses multiple dimensions of difficulty:

Discovery Difficulty
The root cause is not immediately obvious.
Planning Difficulty
The agent must determine an appropriate repair strategy.
Cross-Artifact Reasoning
Correctness depends on relationships between multiple artifacts.
Failure-Mode Complexity
Several individually plausible states may interact incorrectly.
Long-Horizon Execution
Solving the task can require multiple inspection, modification, and
validation steps.
Generalization Difficulty
Correct solutions should satisfy the underlying contract rather than
memorize visible examples.
Preservation Constraints
The agent must repair the failure without breaking unrelated behavior.
Adaptation Difficulty
Intermediate observations and test results may require the agent to
revise its diagnosis or repair strategy.

Difficulty should emerge from reasoning and engineering complexity, not from
broken infrastructure, missing dependencies, or ambiguous task specifications.

Coverage Engineering

A difficult task is not necessarily a good benchmark.

The benchmark therefore considers coverage across multiple dimensions:

Concept coverage
Structural coverage
Semantic coverage
Cross-artifact coverage
Multiple failure modes
Positive and negative cases
Edge cases
Long-tail cases

The objective is to prevent a task from being solved by fixing one superficial
condition while leaving the underlying engineering problem unresolved.

Hidden and Generalization Testing

Where applicable, benchmark designs can use evaluation cases that differ from
the obvious examples exposed during task execution.

Examples include:

Runtime-generated evaluation data
Structural variations
Unseen inputs
Edge cases
Adversarial configurations
Distribution shifts

The purpose is to distinguish genuine reasoning from memorization or
hardcoded solutions.

Oracle-First Validation

Every task follows an Oracle-first development workflow.

Task Design
     ↓
Environment Construction
     ↓
Reference Solution
     ↓
Deterministic Verifier
     ↓
Oracle PASS
     ↓
Coverage PASS
     ↓
Leakage Audit
     ↓
Difficulty Calibration
     ↓
Final Evaluation

A task is not considered ready merely because it appears difficult.

The reference solution must first demonstrate that the task is solvable and
that the verifier correctly recognizes the intended repaired state.

Only after that do we tune difficulty and robustness.

NOP / Baseline Validation

A no-operation baseline is also useful during task validation.

The expected behavior is:

Broken Task
    │
    ├── NOP Agent ───────► FAIL
    │
    └── Oracle Agent ────► PASS

This provides a basic sanity check that the original broken state does not
receive credit without performing the required repair.

Failure-Mode Analysis

The benchmark is designed not only to measure whether an agent succeeds, but
also to expose how agents fail.

Important failure categories include:

Shortcut solutions
Memorization
Partial repairs
Incorrect assumptions
Cross-artifact inconsistencies
State exploitation
Reward hacking
Failure to preserve existing behavior
Incorrect recovery strategies
Concurrency mistakes
Performance regressions

This makes benchmark results more useful for understanding model limitations.

Benchmark Signal

A useful benchmark should separate strong and weak systems rather than simply
producing a difficult-looking score.

We therefore care about:

Score separation
Signal-to-noise ratio
Failure interpretability
Generalization
Robustness
Measurement sensitivity
Avoiding benchmark saturation

The purpose of difficulty is to create informative evaluation signal, not
to maximize failure rates blindly.

Data-Centric Benchmark Design

Task data is treated as part of the evaluation design itself.

Important considerations include:

Concept diversity
Redundancy control
Distribution design
Long-tail cases
Coverage gaps
Structural variation
Generalization budget

Increasing the number of examples alone does not necessarily increase
evaluation quality. Diversity and coverage are often more important than raw
volume.

Representative Task: Kafka Consumer Recovery

One representative task models a distributed Kafka consumer recovery
regression.

The agent must reason across:

Consumer Identity
        ↓
Partition Assignment
        ↓
Generation / Assignment Epoch
        ↓
Committed Offsets
        ↓
Processed Offsets
        ↓
Checkpoint State
        ↓
Restart Policy

The correct repair must restore a coherent recovery contract while preserving:

Consumer identity
Partition topology
Manual commit semantics
Durable committed progress
Partition ownership
Existing workloads
Message accounting

Destructive offset resets and recovery bypasses are rejected.

This is representative of the benchmark philosophy:

The challenge is understanding the system state, not guessing the expected edit.

Representative Task: CUDA Stream/Event Dependencies

Another task models asynchronous CUDA execution across multiple streams.

The intended dependency chain is:

Producer Stream
      │
      │ producer_done
      ▼
Consumer Stream
      │
      │ consumer_done
      ▼
Finalizer Stream

The task requires restoring the correct cross-stream event dependencies while
preserving asynchronous execution.

A global synchronization shortcut is not accepted as an equivalent solution.

This evaluates understanding of CUDA stream/event semantics rather than simple
pattern matching.

Technology Stack

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
│   ├── fastapi-gpu-inference-011/
│   ├── fastapi-idempotency-011/
│   └── fastapi-async-concurrency-009/
│
├── infrastructure/
│   ├── kubernetes-rollout-recovery-010/
│   └── kafka-consumer-offset-recovery/
│
├── algorithms/
│   ├── ml-lp-simplex-optimizer/
│   └── ml-constrained-kkt-optimizer/
│
└── arabic-evaluation/
    └── arabic-count-notification/
Benchmark Engineering Principles

The project follows five core principles:

Correctness over superficial success

A solution must satisfy the underlying engineering contract.

Reproducibility over environment-specific behavior

Tasks are packaged in isolated Docker environments.

Reasoning over pattern matching

Tasks require understanding relationships between artifacts.

Verification over trust

Every repair is independently evaluated.

Real engineering constraints over toy problems

Tasks model failures involving recovery, concurrency, state consistency,
infrastructure, APIs, GPU behavior, and distributed systems.

Portfolio Status

20 tasks currently included.

The portfolio is being developed as a growing collection of reproducible
software-engineering evaluations for AI coding agents and LLM systems.

Future expansion areas include:

CUDA/GPU engineering
Distributed training
Backend infrastructure
Kubernetes and AI infrastructure
Performance engineering
Multilingual evaluation
Additional long-horizon agent tasks
About This Repository

This repository represents an independent benchmark-engineering portfolio built
around Terminal-Bench 3–oriented task architecture, Dockerized execution
environments, independent verifier environments, deterministic evaluation,
reference solutions, cross-artifact reasoning, difficulty engineering, and
anti-leakage design.

The objective is not simply to create difficult coding problems.

The objective is to build reproducible, secure, informative evaluations that
measure whether AI coding agents can perform real software-engineering work.
