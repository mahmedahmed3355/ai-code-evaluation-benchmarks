# Distributed Sharded Checkpoint Recovery

## Incident

A distributed training service saves one checkpoint shard per rank. A recent storage-path refactor introduced a recovery bug: a worker can observe a checkpoint directory that contains some new shards but not all shards, and the resume logic can select that incomplete step as the latest checkpoint.

This is especially dangerous after a worker restart: training may resume from a mixed global state even though every individual shard file is syntactically valid.

## Your task

Repair the checkpoint commit and recovery protocol so that a checkpoint becomes visible to recovery **only after every expected rank shard has been durably published and the checkpoint manifest describes exactly that complete set**.

The implementation must support the existing multi-rank layout and preserve the public Python API.

### Required behavior

1. Each checkpoint step has exactly `world_size` rank shards: `rank-<N>.json`.
2. A shard must first be written to a temporary/staging path and atomically published to its final name.
3. Recovery must never select a step with missing, duplicated, or unexpected rank shards.
4. The manifest is the commit record. It must be published only after all expected shards are present and validated.
5. Recovery must validate the manifest against the checkpoint directory instead of trusting the manifest blindly.
6. A newer incomplete step must not hide an older complete step.
7. A corrupt or incomplete newest checkpoint must be ignored and recovery must return the newest valid complete checkpoint.
8. Existing complete checkpoints must remain recoverable after a failed commit attempt.
9. The checkpoint payload is opaque application state; do not hard-code its values.
10. Keep the existing public interfaces in `environment/app/checkpoint.py` and do not modify the test harness.

### Constraints

- CPU-only; no network and no external services.
- Do not change the checkpoint directory schema.
- Do not delete or rewrite historical complete checkpoints as a shortcut.
- Do not make recovery depend on a fixed step number or the fixture's exact payload values.
- Do not bypass validation by returning a hard-coded checkpoint.

## Acceptance

Run:

```bash
/app/validate.sh
```

A correct repair must report `VALIDATION=PASS`.
