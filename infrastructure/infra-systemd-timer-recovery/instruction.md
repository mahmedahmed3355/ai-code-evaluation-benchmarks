# Task: Recover a migrated systemd maintenance job

A maintenance worker was migrated from cron to systemd timer/service units. The migration introduced duplicate execution and incorrect recovery from stale run state.

Repair the infrastructure configuration so the existing maintenance application satisfies its operational contract.

## Required behavior

1. Only one maintenance run may be active.
2. A second invocation while the owner is alive must not steal the lock or modify its state.
3. A lock left by a crashed owner may be recovered when its ownership metadata proves the owner is inactive.
4. A successful run must publish completion state.
5. A failed run must remain a failure; it must not publish success.
6. Missed timer events must be reconsidered after boot.
7. The timer/service must not intentionally overlap runs.
8. Preserve the existing application command.
9. Preserve the non-root identity, memory limit, CPU weight, and timeout.
10. Preserve the lock metadata format and job generation semantics.

## Constraints

Do not:

- edit `app/maintenance.py`;
- edit the validator or tests;
- delete the lock unconditionally;
- ignore owner liveness;
- allow concurrent runs;
- turn failures into successful exits;
- disable persistent scheduling;
- remove timeout protection;
- run the application as root;
- replace the application with a shell success command;
- hard-code a PASS result.

The evaluator uses alternate job generations and ownership states. Do not special-case the supplied example.

Run:

```bash
./validate.sh
```

and finish with `VALIDATION=PASS`.
