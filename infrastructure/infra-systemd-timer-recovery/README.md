# infra-systemd-timer-recovery-014

## Incident

A production maintenance job was migrated from a cron-based launcher to a systemd timer.

After the migration, operators observed two failure modes:

1. the job can start twice when a previous run is still active;
2. a failed run can leave stale state that causes the next scheduled run to be skipped.

The service must provide the same operational semantics as the old launcher while using the new systemd model.

This benchmark models the service/timer contract deterministically. It does not require a live systemd PID 1.

## Operational contract

The maintenance job has these properties:

- one active run at a time;
- a successful run records a completion generation;
- a failed run must remain observable and must not be mistaken for success;
- a stale lock from a crashed process may be recovered only when ownership metadata proves that the owner is no longer active;
- a live owner must never be stolen;
- a scheduled invocation that finds a live owner must exit without corrupting the active run;
- a timer must not create overlapping service instances;
- persistent scheduling is required so a missed timer event is reconsidered after boot;
- resource, identity, and timeout requirements are part of the contract.

## Why this is hard

The visible symptom is "maintenance did not run", but several tempting repairs are incorrect:

- deleting every lock before starting;
- treating every old lock as stale;
- allowing concurrent execution;
- converting every failure to success;
- disabling persistence;
- removing timeout protection;
- changing the application command.

The evaluator tests crash recovery, live-owner protection, stale-owner recovery, duplicate invocations, missed schedules, failure propagation, alternate job generations, and security/resource invariants.

The intended repair is in the launcher/timer configuration and lock protocol, not in the maintenance application.

## Validation

The environment is CPU-only and deterministic.

```bash
./validate.sh
```

A correct repair ends with:

```text
VALIDATION=PASS
```
