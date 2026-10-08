# Production CDC Sink — Recovery + Schema Evolution

Implement a production-style change-data-capture sink in `/app/cdc_sink.py`.

The program is invoked as:

```bash
python /app/cdc_sink.py --events /app/data/events.jsonl --state-dir /app/state
```

It must be safe to run repeatedly against the same state directory. A successful invocation
must process every valid event that can be processed in order and persist the resulting state.

## 1. Input events

The input is JSON Lines. Each non-empty line must be one JSON object with:

- `partition`: non-negative integer
- `offset`: non-negative integer
- `key`: non-empty string
- `op`: `"upsert"` or `"delete"`
- `schema_version`: positive integer
- `payload`: JSON object for `upsert`, or `null` for `delete`

Offsets are scoped to a partition. The first accepted offset for a partition is `0`.
For an already initialized partition, the next accepted offset is exactly the last
successfully committed offset + 1.

Events can be interleaved across partitions. Partition A being at offset 10 does not
prevent partition B from accepting offset 3.

## 2. Sink state

Persist materialized records in:

`<state-dir>/records.json`

The file is a JSON object mapping keys to records. A record contains the latest fields
for that key plus these metadata fields:

```json
{
  "...user fields...": "...",
  "_key": "customer-1",
  "_schema_version": 2
}
```

`_key` and `_schema_version` are reserved and must never be supplied by event payloads.

Persist per-partition checkpoints in:

`<state-dir>/checkpoint.json`

Its normal shape is:

```json
{
  "partitions": {
    "0": 7,
    "1": 3
  }
}
```

The checkpoint value is the highest successfully committed offset for that partition.
A partition that has never accepted an event is absent.

## 3. At-least-once + idempotent replay

Treat the sink as at-least-once.

For an event whose offset is greater than the committed offset, apply its effect to
`records.json` and then durably advance the checkpoint.

If the same event is delivered again after its effect was applied but before its
checkpoint was persisted, replay MUST NOT apply the business effect twice.

Therefore processing must be idempotent with respect to `(partition, offset)`.

An event with `offset <= checkpoint[partition]` is an already committed replay and must
be ignored. It must not mutate records or checkpoints.

Do not deduplicate only by key: two different offsets for the same key are legitimate
updates.

## 4. Gap detection

If a partition has no checkpoint, only offset `0` is accepted.

If a partition has checkpoint `N`, only offset `N + 1` is accepted.

An event with an offset greater than the expected offset is a gap and must be rejected
without changing records or the checkpoint.

An event with an offset lower than or equal to the checkpoint is a replay and must be
handled as described above.

A gap in one partition must not prevent valid processing in another partition.

## 5. Operations

### Upsert

`op="upsert"` applies a partial update.

Only fields present in `payload` are changed. Existing fields not present in the payload
remain unchanged.

A new key starts from an empty record.

### Delete / tombstone

`op="delete"` is a tombstone. Its payload must be `null`.

Deleting an existing key removes the materialized record. Deleting a key that is already
absent is still a valid idempotent business effect.

The checkpoint must advance for a valid delete.

## 6. Schema registry and additive evolution

The supplied registry is:

`/app/data/schema_registry.json`

It maps schema versions to field definitions. Example:

```json
{
  "1": {"id": "string", "name": "string", "balance": "number"},
  "2": {"id": "string", "name": "string", "balance": "number", "email": "string"}
}
```

A schema version is valid only if it exists in the registry.

Schema evolution is allowed only when the new schema is additive relative to the previous
schema version used by that partition:

- existing fields must keep the same type;
- fields may be added;
- fields may not be removed;
- an existing field's type may not change.

The first event of a partition may use any registered schema version.

For an event after the first one, its schema version must be equal to or greater than the
partition's previous schema version. A downgrade is invalid.

The event payload may contain only fields declared by its schema version and may not
contain `_key` or `_schema_version`.

A malformed schema transition must be rejected without mutating records or checkpoints.

Important: schema state is tracked per partition, not globally. Different partitions can
legitimately be at different schema versions.

## 7. Validation / malformed input

Reject an event if:

- it is not a JSON object;
- required fields are missing or have the wrong basic type;
- partition/offset/schema_version are invalid;
- key is empty;
- op is unknown;
- delete has a non-null payload;
- upsert does not have an object payload;
- payload contains reserved metadata fields;
- payload contains a field not present in its schema;
- a payload value has the wrong type for its declared field;
- schema_version is unknown;
- schema evolution violates the additive-only rules;
- the event creates an offset gap.

Rejected events must not change records or checkpoints.

The implementation must continue scanning the input after a rejected event so that valid
events for other partitions can still be processed. However, for a partition with a
rejected event at its expected offset, later offsets in that same partition remain gaps
and must not be accepted.

The program should exit with status 0 when the file was processed; rejection is reported
in `/app/state/rejections.jsonl`. Do not abort the whole run because of one malformed
event.

Each rejection line should contain at least:
`partition`, `offset` when available, and a short `reason`.

## 8. Corrupt checkpoint recovery

The checkpoint is important but must not be trusted blindly.

If `checkpoint.json` is missing, treat it as an empty checkpoint.

If it is invalid JSON, has the wrong shape, contains negative/non-integer offsets, or has
non-string partition keys representing non-negative integers, recover by rebuilding the
checkpoint from the durable journal:

`<state-dir>/commit_journal.jsonl`

Each committed journal line has the form:

```json
{"partition": 0, "offset": 7}
```

The journal records effects that were durably committed before the checkpoint write.

During recovery, use the longest contiguous prefix starting at offset 0 for each partition.
Do not jump over missing offsets merely because a larger journal offset exists.

The recovered checkpoint must then be rewritten atomically.

If the journal itself contains malformed lines, ignore malformed journal lines but do not
invent offsets.

## 9. Crash/re-entrant semantics

The implementation must use atomic file replacement for durable JSON state where practical
(e.g. write a temporary file and `os.replace` it).

The order of a normal commit is:

1. validate the event;
2. apply the business effect;
3. append the `(partition, offset)` commit to the journal and flush it;
4. persist the checkpoint atomically.

If execution stops after step 3 and before step 4, the next run must recover the committed
offset from the journal and must not re-apply the business effect.

You may use the journal to make replay decisions, but do not rely on process-local memory.

The implementation must be re-entrant: running the command multiple times over the same
input and state directory must converge to exactly the same records/checkpoints.

## 10. Concurrency and corruption safety

You do not need to implement multi-process locking. Tests invoke one process at a time.

Do not rewrite unrelated partitions when committing an event.

Never silently reset a non-empty state directory just because a file is malformed.

The implementation must handle large JSONL streams without loading the entire event stream
into memory.

## Deliverable

Create `/app/cdc_sink.py`. No external Python packages are required.

The evaluator will use public and hidden event streams, including:
- multi-partition interleaving;
- repeated delivery;
- crash-after-effect recovery;
- tombstones;
- partial updates;
- schema-version boundaries;
- additive evolution;
- invalid removals/type changes;
- malformed JSON/events;
- corrupt checkpoints;
- sparse/corrupt journals;
- large streams;
- re-entrant execution.

Do not hardcode the supplied fixture, expected final records, offsets, or test-specific keys.
