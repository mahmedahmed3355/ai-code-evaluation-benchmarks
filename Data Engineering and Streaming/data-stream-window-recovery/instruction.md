# Repair the production event-stream aggregation pipeline

A streaming analytics worker consumes an **at-least-once** event feed and maintains durable five-minute event-time aggregates. The worker was damaged during a recovery refactor. Your job is to repair the implementation in `environment/streaming/` so that it obeys the persisted streaming contract.

## Required behavior

1. Use `event_time`, never arrival order or wall-clock time, to assign events to five-minute windows.
2. Compute the watermark as `max_event_time_seen - allowed_lateness_seconds`.
3. Delivery is at-least-once. `event_id` is the stable idempotency key. The same event ID must contribute at most once, even if a later delivery has different payload fields.
4. An event may update a window while that window is still open. Once a window is finalized by the watermark, later events for that window are **not allowed to mutate the aggregate**; route them to the durable DLQ with a reason and source offset.
5. Recovery must tolerate a crash after durable state was written but before the offset was advanced. Replaying those records must be idempotent.
6. The checkpoint is trusted only when it represents the `state_then_offset` commit protocol. Invalid checkpoint metadata must fail closed rather than silently resetting to earliest/latest.
7. Persist state and checkpoint atomically enough that a restart cannot create a partially written JSON document. Temporary files may be used.
8. The output is a deterministic projection of finalized windows only. Re-running the worker must not duplicate aggregates or DLQ records.
9. Preserve the supplied configuration and event payloads. Do not delete data, rewrite event history, disable deduplication, or bypass the checkpoint.
10. Do not add external services, Kafka dependencies, network calls, or hard-coded answers for the supplied fixture.

## Files

- `environment/streaming/processor.py` — broken implementation to repair.
- `environment/streaming/cli.py` — command-line entry point.
- `environment/data/events.jsonl` — representative at-least-once event feed.
- `environment/data/state.json` — durable aggregate state at restart.
- `environment/data/checkpoint.json` — durable consumer checkpoint.
- `environment/data/config.json` — streaming contract.

You may add small helper modules under `environment/streaming/`, but keep the public CLI contract unchanged.

## Validation

The evaluator exercises normal, reordered, duplicated, late, boundary, restart, malformed, large, and adversarial streams. It also checks artifact immutability, deterministic output, checkpoint ordering, idempotent replay, and fail-closed recovery.

A correct solution must generalize beyond the visible fixture. Do not hard-code event IDs, offsets, window totals, or expected output.
