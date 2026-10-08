# data-cdc-sink-recovery-019

Hard Terminal-Bench task: Production CDC Sink + Recovery + Schema Evolution.

Coverage:
- CDC event processing
- per-partition offsets
- at-least-once delivery
- idempotent replay
- crash-after-effect recovery through durable journal
- gap detection
- tombstones/deletes
- partial updates
- additive schema evolution
- per-partition schema versions
- corrupt checkpoint recovery
- multi-partition interleaving
- re-entrant execution
- malformed/adversarial events
- large streams
- anti-hardcoding
- independent model-based verifier

Validation target:
- 11 public tests
- 10 hidden/adversarial tests
- 1 independent verifier
