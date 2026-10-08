# FastAPI Async Concurrency — Task 009

## Incident

A FastAPI service experienced a concurrency regression after blocking work was placed directly inside an `async` endpoint. The API still returns correct results, so a superficial functional test passes, but concurrent requests serialize on the event loop.

The task is to repair the concurrency boundary without changing the public API or hiding the underlying blocking operation.

## What this evaluates

- Python `asyncio` event-loop semantics
- FastAPI request handling
- isolation of blocking work from an event loop
- concurrent request reasoning
- preservation of an existing API contract
- safe refactoring of production-style code

## Constraints

The workload and verifier are immutable from the agent's perspective. The repair must remain general for arbitrary `delay_ms` values rather than special-casing the supplied benchmark.

## Verification

The verifier combines API and source-structure checks, async endpoint checks, preservation of `blocking_operation`, concurrent execution of four independent requests, response correctness, and shortcut resistance.

The reference solution demonstrates one valid repair, but the verifier evaluates behavior and invariants rather than requiring a particular implementation string.

## Runtime

CPU-only, deterministic, no network access required. The environment runs FastAPI/Uvicorn on Python 3.12.

## Expected engineering decision
The core issue is not the HTTP layer itself; it is where blocking work executes relative to the event loop. A correct repair may use any appropriate standard concurrency boundary as long as the observable contract and general behavior are preserved.
