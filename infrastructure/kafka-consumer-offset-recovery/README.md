# Kafka Consumer Recovery Repair

## Overview

This task evaluates an agent's ability to diagnose and repair a deterministic Kafka consumer recovery-state regression.

The scenario involves a consumer group processing multiple partitions with explicit offset commits. A restart/rebalance has left several pieces of recovery state inconsistent across the supplied configuration and recovery artifacts.

The agent must inspect the available state, reason about the recovery contract, and make a minimal coherent repair while preserving the existing processing semantics.

## What the Task Tests

The task evaluates reasoning about:

- Kafka consumer-group state
- Manual offset commit semantics
- Processed versus durable committed offsets
- Consumer generation consistency
- Assignment epoch consistency
- Partition ownership
- Restart recovery state
- Recovery checkpoints
- Cross-artifact state consistency
- Preservation of workload accounting

## Constraints

The repair must preserve:

- Consumer identity
- Topic and partition topology
- Manual commit behavior
- Existing partition ownership
- Existing workloads
- Existing message and commit accounting
- Recovery semantics

Destructive offset resets and recovery bypasses are not valid solutions.

## Verification

The verifier checks the repaired state through independent invariants spanning the supplied artifacts. It validates recovery consistency, partition ownership, durable progress, workload preservation, and safe recovery behavior.

The environment intentionally does not expose the verifier implementation or reference solution to the agent.

## Difficulty

The task is designed as a distributed-state debugging problem rather than a single-value configuration edit. Correct repair requires correlating multiple artifacts and preserving invariants across the recovery state.
