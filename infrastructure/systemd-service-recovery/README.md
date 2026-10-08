# systemd-service-recovery-013

## Incident

A production worker was migrated to a new configuration layout. After reboot, the service can enter a failed state even though the application binary and configuration are valid.

The incident involves several real systemd contracts that interact:

- configuration must be loaded before the worker starts;
- the network dependency must be ordered correctly;
- configuration errors must fail before the worker is launched;
- transient worker failures should recover without creating an uncontrolled restart loop;
- a readiness marker is only valid after the worker has started successfully;
- a clean shutdown must not be treated as a crash;
- the unit must retain least-privilege and resource-limit requirements.

The supplied environment is a deterministic model of these contracts. It does not require a real PID 1 or a live network.

## What makes this task difficult

The visible symptom is simply `service=FAILED`, but there are multiple plausible repairs. A good repair must preserve the existing deployment contract rather than disabling the checks.

The evaluator exercises:

1. cold boot;
2. configuration validation failure;
3. transient application failure;
4. repeated failure / restart throttling;
5. clean stop;
6. readiness publication;
7. dependency ordering;
8. resource and security invariants;
9. alternate configuration values.

A solution that merely changes the final status to `ACTIVE` is insufficient.

## Repository contract

Do not modify:

- `app/worker.py`
- `runtime/reference_contract.json`
- `runtime/workloads.json`
- `tests/`
- the reference implementation.

The intended repair belongs in the service unit and its drop-in configuration.

## Running locally

```bash
cd /app
./validate.sh
```

The validator is CPU-only, deterministic, and does not access the network.
