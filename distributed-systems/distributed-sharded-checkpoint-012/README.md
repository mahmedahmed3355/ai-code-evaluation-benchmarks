# distributed-sharded-checkpoint-011 — Atomic Distributed Checkpoint Commit & Recovery

Forge Bench benchmark task for distributed-training infrastructure.

## Scenario

A training job uses rank-local checkpoint shards. A storage refactor accidentally made recovery trust the newest directory/manifest even when that checkpoint was only partially committed. The resulting failure is a classic distributed-systems problem: every file can look valid while the **global checkpoint state is inconsistent**.

The agent must repair the commit/recovery protocol, not merely patch the fixture.

## What makes it difficult

The failure spans several interacting invariants:

- rank-shard completeness
- atomic publication
- manifest-as-commit-record semantics
- recovery of the newest valid checkpoint rather than the newest directory
- rejection of missing/extra/duplicate/corrupt shards
- preservation of older checkpoints after failed commits
- opaque payload handling

The task intentionally contains plausible wrong repairs, such as accepting any manifest, choosing the largest step directory, or treating a syntactically valid partial checkpoint as complete.

## Evaluation

The verifier checks normal recovery plus adversarial states including:

- missing rank shard
- extra rank shard
- corrupt shard
- stale/incomplete manifest
- newer incomplete checkpoint above an older complete checkpoint
- alternate world sizes and step numbers
- opaque payload changes
- source/harness tampering attempts

The reference solution is independent of fixture payload values.

## Runtime

- Python 3
- Docker
- CPU only
- deterministic
- no network

## Task contract

The public API is intentionally small. The benchmark evaluates behavior through the existing checkpoint manager and does not require a specific implementation technique beyond the atomic publication and validation invariants described in `instruction.md`.
