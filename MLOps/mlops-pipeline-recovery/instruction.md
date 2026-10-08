# MLOps — Recoverable DAG Pipeline Controller

Implement `/app/pipeline.py`.

Invocation:

```bash
python /app/pipeline.py --pipeline /app/data/pipeline.json   --events /app/data/events.jsonl --state-dir /app/state --out /app/decision.json
```

This task models a production ML pipeline controller. It must be deterministic and
re-entrant.

## Pipeline

The pipeline is a DAG of stages. Each stage has:
- `name`
- `depends_on`
- `retry_limit`
- `artifact`
- `timeout_seconds`

The artifact descriptor has `path` and `sha256`.

A stage is runnable only when every dependency is `SUCCEEDED`.

## Durable state

State directory:
- `checkpoint.json`
- `journal.jsonl`

Checkpoint shape:

```json
{
  "stages": {
    "prepare": {"status":"SUCCEEDED","attempts":1,"artifact_sha256":"..."},
    "train": {"status":"RUNNING","attempts":2}
  }
}
```

The journal is authoritative for recovery. Each valid line is:

```json
{"stage":"train","status":"SUCCEEDED","attempt":2,"artifact_sha256":"..."}
```

Malformed journal lines must be ignored.

If checkpoint is missing/corrupt, rebuild stage state from the journal using the latest
valid transition per stage, but never invent a success without a matching artifact.

## Event semantics

Input events represent external executor outcomes:
- `STARTED`
- `SUCCEEDED`
- `FAILED_RETRYABLE`
- `FAILED_TERMINAL`

For each event:
- stage must exist;
- attempt must be a positive integer;
- attempt cannot decrease;
- `SUCCEEDED` requires artifact checksum to match the declared artifact;
- `FAILED_TERMINAL` makes the stage permanently failed;
- `FAILED_RETRYABLE` can be retried while `attempts < retry_limit`.

Duplicate delivery of an already committed event must be a no-op.

A success for a stage whose dependencies were not succeeded is invalid and must not advance
state.

## One decision per run

After replaying all events, output:

```json
{
  "action":"run|wait|blocked|failed|noop",
  "stage":"name-or-null",
  "attempt":1,
  "reason":"...",
  "pipeline_status":"RUNNING|SUCCEEDED|FAILED"
}
```

Decision rules:

1. If any stage is terminally failed -> `failed`.
2. If every stage succeeded -> `noop`, pipeline `SUCCEEDED`.
3. Choose a runnable pending stage whose dependencies all succeeded.
4. If a stage is `FAILED_RETRYABLE` and attempts < retry_limit, choose it before any
   untouched stage.
5. Otherwise choose the lexicographically smallest runnable stage name.
6. The chosen action is `run` with attempt = previous attempts + 1.
7. If no stage is runnable because dependencies are incomplete, return `wait`.
8. If a dependency is terminally failed, downstream stages are `blocked`.

## Artifact integrity

The controller must never trust a supplied success checksum.
It must calculate SHA256 from the artifact file.

An artifact may be produced by a stage and consumed by another stage. If the file is missing
or its checksum does not match, the producing stage cannot be considered successfully
committed.

## Recovery / idempotency

The expected sequence is:
1. validate an event;
2. append valid transition to journal and flush;
3. atomically rewrite checkpoint.

If checkpoint write was lost, replaying the journal must recover the state.

Repeated execution over the same inputs must produce byte-identical `decision.json` and must
not duplicate journal transitions.

Do not truncate or reset a non-empty journal because the checkpoint is corrupt.

## Hidden adversarial cases

- duplicate STARTED/SUCCEEDED events;
- out-of-order events;
- success before dependency completion;
- checksum mismatch;
- corrupt checkpoint;
- malformed journal;
- retry-limit boundary;
- terminal failure propagation;
- diamond DAGs;
- lexicographic tie breaking;
- missing artifact;
- large event streams;
- re-entrant execution;
- fake checksum fields;
- stages whose names are intentionally adversarial.
