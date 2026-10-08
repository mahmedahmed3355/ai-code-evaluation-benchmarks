# Distributed Systems

**4 benchmark tasks**

This domain covers distributed training, checkpoint commit protocols and concurrency-sensitive FastAPI behavior.

| Task | Difficulty | Focus |
|---|---|---|
| `distributed-ddp-accumulation-010` | Hard | DDP weighting, uneven ranks, checkpoint/resume |
| `distributed-sharded-checkpoint-012` | Hard | Atomic sharded checkpoint publication/recovery |
| `fastapi-async-concurrency-009` | Medium | Event-loop blocking and genuine async overlap |
| `fastapi-idempotency-011` | Hard | Concurrent same-key requests and exactly-once creation |

## Evaluation themes

Tasks are designed so process-local shortcuts, serialized behavior and destructive recovery strategies fail hidden or concurrent cases.

## Difficulty

**Hard: 3**  
**Medium: 1**
