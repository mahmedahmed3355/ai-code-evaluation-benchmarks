# Kubernetes / Cloud Systems — Production Rollout Reconciler

Implement `/app/reconcile.py`.

Invocation:

```bash
python /app/reconcile.py --spec /app/data/spec.json --state /app/data/cluster_state.json --out /app/out.json
```

The program is a deterministic, offline Kubernetes-like rollout planner. It must NOT call
a real Kubernetes API or assume kubectl is installed.

Your job is to compute the next safe reconciliation plan for a Deployment-like workload
while respecting scheduling, readiness, PodDisruptionBudget, topology-spread and rollout
constraints.

The evaluator will provide hidden cluster states and workload specs.

## Input

`spec.json`:

```json
{
  "workload": {
    "name": "payments",
    "namespace": "prod",
    "replicas": 5,
    "max_unavailable": 1,
    "max_surge": 1,
    "min_ready_seconds": 2,
    "revision": "r2",
    "rollback_revision": "r1"
  },
  "pod_template": {
    "labels": {"app":"payments","tier":"api"},
    "requests": {"cpu_m": 500, "memory_mib": 512},
    "readiness": {"required": true}
  },
  "pdb": {
    "min_available": 4
  },
  "topology": {
    "key": "zone",
    "max_skew": 1
  },
  "policy": {
    "allow_preemption": false,
    "allow_rollback": true
  }
}
```

`cluster_state.json` contains:

```json
{
  "nodes": [
    {
      "name": "n1",
      "zone": "a",
      "ready": true,
      "allocatable": {"cpu_m": 2000, "memory_mib": 4096},
      "used": {"cpu_m": 500, "memory_mib": 512}
    }
  ],
  "pods": [
    {
      "name": "payments-old-0",
      "workload": "payments",
      "revision": "r1",
      "node": "n1",
      "ready": true,
      "ready_for_seconds": 30,
      "terminating": false
    }
  ]
}
```

Pods may contain extra fields. Ignore fields not relevant to the contract.

## Core objective

Return `/app/out.json`:

```json
{
  "action": "create|delete|wait|rollback|noop|reject",
  "pod": "deterministic-name-or-null",
  "node": "node-or-null",
  "reason": "short machine-readable reason",
  "desired_revision": "r2",
  "available_replicas": 5,
  "total_replicas": 6,
  "old_replicas": 1,
  "new_replicas": 5
}
```

The exact fields above must always exist.

The planner makes ONE reconciliation decision per invocation. It must not mutate
`cluster_state.json`.

## 1. Desired replicas and revisions

- `replicas` is the desired steady-state count.
- Pods of `revision == workload.revision` are NEW.
- Pods of any other revision belonging to the workload are OLD.
- Pods with `terminating == true` count toward total pods until termination, but do not
  count as available.
- A ready pod counts as available only if:
  - `ready == true`;
  - `terminating == false`;
  - its node exists and is ready;
  - `ready_for_seconds >= min_ready_seconds`.

## 2. Rollout capacity

Let:
- desired = `replicas`
- max_surge = `max_surge`
- max_unavailable = `max_unavailable`

During a rollout:
- total pods must never exceed `desired + max_surge`;
- available pods must never fall below `desired - max_unavailable`;
- max_unavailable is never allowed to make the availability floor negative.

Prefer creating a new pod when capacity exists and a valid placement exists.
Prefer deleting one OLD available pod when the new revision has enough availability to
preserve the availability floor.

Never delete a NEW pod merely to make room for another NEW pod.

Never delete an OLD pod that is required to maintain the availability floor.

## 3. Scheduling / resource feasibility

A newly created pod requires the full request from `pod_template.requests`.

A node is feasible only when:
- node `ready == true`;
- remaining CPU >= requested CPU;
- remaining memory >= requested memory.

Do not schedule onto a node that lacks either resource.

The planner must account for existing pods' resource requests when those requests are
present on the pod object as `requests`. If absent, assume zero for accounting.

A terminating pod still consumes resources until it disappears.

Do not use aggregate cluster capacity as a substitute for per-node feasibility.

## 4. Topology spread

If topology is present:

```json
{"key":"zone","max_skew":1}
```

count all non-terminating workload pods by topology value.

A candidate node is invalid if adding the new pod would make:

`max(counts) - min(counts) > max_skew`

across topology domains represented by eligible nodes.

If a topology domain currently has zero workload pods, it participates in the minimum.

When multiple feasible nodes remain, choose the node that produces the smallest resulting
topology skew, then the node with the most remaining CPU, then lexicographically smallest
node name.

## 5. PodDisruptionBudget

A PDB with `min_available` requires:

`available_after_action >= min_available`

for deletion actions.

If there is no PDB, there is no additional PDB constraint.

A PDB never permits deleting an unavailable pod to manufacture capacity.

## 6. Readiness and startup behavior

A pod that is running but not ready is NOT available.

A pod whose `ready_for_seconds` is below `min_ready_seconds` is NOT available even if
`ready == true`.

Therefore a rollout may need to return:

```json
{"action":"wait", ...}
```

instead of deleting an old pod.

If a NEW pod is pending/not-ready and there is no safe action that can improve the rollout,
wait.

## 7. Deterministic pod naming

New pod names must be:

`<workload>-<revision>-<ordinal>`

where `<ordinal>` is the smallest non-negative integer not already used by any pod of the
same workload and revision.

Do not reuse an existing name.

## 8. Decision priority

Use this deterministic priority:

### A. Reject
Return `reject` if the input contract itself is invalid:
- missing required sections;
- negative replicas/surge/unavailable;
- invalid node resources;
- duplicate pod names;
- workload pod references a missing node;
- unknown topology key on nodes;
- `max_surge` / `max_unavailable` not integers;
- request values invalid.

### B. No-op
If new replicas == desired and there are no old replicas, return `noop`.

### C. Rollback
If:
- desired revision has zero available NEW pods;
- OLD pods exist;
- `allow_rollback == true`;
- `rollback_revision` exists among the OLD revisions;
- and the desired revision cannot currently make progress because there is no feasible
  node for a new pod;

then return `rollback`.

Rollback means setting `desired_revision` in the output to `rollback_revision`; do not
pretend that a rollback pod was actually created.

### D. Create
If total replicas < desired + max_surge and a feasible topology-valid node exists,
create exactly one NEW pod.

### E. Delete
If total replicas > desired OR old replicas > 0, delete exactly one OLD pod only if:
- it is non-terminating;
- deleting it preserves both rollout availability floor and PDB min_available;
- after deletion, there are enough NEW available pods that the rollout can safely
  progress.

Prefer deleting the oldest OLD pod by `age_seconds` descending, then lexicographically
by name.

### F. Wait
Otherwise wait.

## 9. Anti-shortcut requirements

Do not hardcode:
- node names;
- zones;
- workload names;
- replica counts;
- revisions;
- expected pod names;
- the supplied fixture's final action.

Do not assume there are exactly two zones or two nodes.

Do not sort nodes solely by name when a topology/resource score is required.

Do not use aggregate CPU/memory to bypass per-node placement.

Do not treat readiness as equivalent to existence.

Do not ignore terminating pods.

Do not mutate input files.

## 10. Output determinism

Output JSON with stable keys and deterministic values.

For `create`:
- `action = "create"`
- `pod` = generated name
- `node` = selected node

For `delete`:
- `action = "delete"`
- `pod` = selected old pod
- `node` = its node

For `wait`, `rollback`, `noop`, `reject`:
- `pod = null`
- `node = null`

`reason` must be one of:
- `invalid_input`
- `rollout_complete`
- `surge_capacity_available`
- `old_pod_safe_to_remove`
- `waiting_for_readiness`
- `waiting_for_capacity`
- `waiting_for_topology`
- `rollback_unavailable`
- `rollback_due_to_unschedulable_revision`

The evaluator will use public and hidden cases for:
- multi-node scheduling;
- CPU/memory fragmentation;
- topology skew;
- terminating pods;
- readiness delays;
- PDB floors;
- maxSurge/maxUnavailable boundaries;
- mixed old/new revisions;
- deterministic naming;
- rollback;
- malformed specs;
- large pod sets;
- adversarial node ordering;
- re-entrant identical inputs.
