# Infrastructure

**4 benchmark tasks**

Infrastructure tasks model operational recovery and state reconciliation across systemd, Kafka and Kubernetes.

| Task | Difficulty | Focus |
|---|---|---|
| `infra-systemd-timer-recovery` | Hard | Locking, crash recovery, scheduling, resource/security contracts |
| `kafka-consumer-offset-recovery` | Hard | Durable commits, generation/epoch consistency, restart recovery |
| `kubernetes-rollout-recovery` | Hard | Cross-resource selectors, rollout identity and availability |
| `systemd-service-recovery` | Hard | Startup ordering, readiness, restart policy, security |

`infrastructure/modules/` contains supporting infrastructure modules and is not a benchmark task.

## Difficulty

**Hard: 4 / 4**
