# Data Streaming: Event-Time Window Recovery & Exactly-Once Effects

A production-style benchmark for AI coding agents repairing a durable streaming aggregation worker.

## Scenario

An analytics consumer processes an **at-least-once** event stream and emits five-minute event-time aggregates. During a recovery refactor, several correctness guarantees were broken at once: delivery duplicates can be double-counted, the watermark is derived incorrectly, finalized windows can be mutated, and the checkpoint/state ordering is unsafe during crashes.

The task is intentionally implemented as a local deterministic stream processor rather than requiring a live Kafka cluster. The state/checkpoint files model the durable boundary a real consumer would maintain.

## What the agent must reason about

- Event time versus arrival/processing time
- Watermarks and bounded lateness
- Stable event-ID deduplication under at-least-once delivery
- Finalized-window immutability
- Dead-letter routing for data that arrives after finalization
- Crash recovery when durable state is ahead of the committed offset
- State-before-offset commit ordering
- Atomic persistence and re-entrant execution
- Deterministic materialization of finalized aggregates
- Fail-closed handling of corrupt checkpoint/configuration metadata

## Why this is hard

The failures interact. A superficially plausible fix can pass nominal aggregation while still double-counting replayed records, reopening finalized windows, trusting an unsafe checkpoint, or producing duplicate DLQ entries. Hidden tests vary event order, duplicate payloads, timestamps, window boundaries, checkpoint positions, state generations, cardinality, numeric values, malformed records, and restart conditions.

The benchmark deliberately avoids a single magic expected output. Correctness is expressed through invariants that should hold for arbitrary compatible streams.

## Evaluation contract

The package contains:

- a broken CPU-only environment;
- a reference solution;
- public regression tests;
- a large adversarial hidden suite;
- an independent structural verifier;
- Dockerized evaluation with no network dependency.

The evaluator never needs a real Kafka broker. The task models the durable semantics that a production consumer must preserve.

## Anti-shortcut requirements

Solutions that hard-code fixture totals, event IDs, offsets, or output files will fail hidden permutations and generated streams. The evaluator also checks source/configuration preservation and fail-closed recovery behavior.

## Expected expert profile

Strong candidates should understand streaming semantics, distributed-systems recovery, idempotency, durable checkpoints, event-time processing, and production Python.

**Category:** Data Engineering / Streaming  
**Runtime:** CPU-only, deterministic  
**Difficulty:** Hard  
**Expected expert time:** 60–100 minutes
