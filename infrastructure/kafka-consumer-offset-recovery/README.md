# Kafka Consumer Offset Recovery — Infrastructure Benchmark

A realistic infrastructure/debugging task for an AI coding agent.

## Scenario

An inference consumer group restarted during a rebalance. Several lifecycle artifacts were persisted independently:

- active consumer assignment
- restart metadata
- checkpoint
- per-partition processing state
- durable commit journal
- workload accounting

The incident is subtle because the processed position is ahead of the durable committed position on one partition, while generation/epoch metadata is inconsistent across artifacts.

The correct repair is to reconstruct the recovery contract from the persisted state and repair only the corrupted recovery metadata.

## What this evaluates

- Kafka consumer-group recovery reasoning
- committed vs processed offset semantics
- generation/assignment-epoch consistency
- partition ownership
- checkpoint correctness
- crash/restart recovery
- durable commit evidence
- preservation of workload/accounting state
- avoidance of destructive offset-reset shortcuts

## Why it is difficult

No single value tells the whole story. Several individually plausible values conflict across files. A naive agent can easily:

- resume from a processed-but-uncommitted offset
- accept stale generation/epoch metadata
- rewrite historical processed/committed state
- reset to latest/earliest
- delete a partition to remove the inconsistency
- modify workloads to make accounting pass

Those repairs are explicitly invalid.

## Validation

The task includes:

- a reference/oracle solution
- deterministic independent verifier
- hidden adversarial checks
- baseline regression checks
- cross-artifact invariants
- preservation checks

No Kafka service or external network is required.

## Deliverable

The agent edits only the persisted recovery state and leaves the consumer contract and workload artifacts intact.

## Benchmark metadata

**Category:** Infrastructure / Distributed Systems  
**Runtime:** CPU-only, deterministic  
**Difficulty:** Hard  
**Expected expert time:** ~45–75 minutes
