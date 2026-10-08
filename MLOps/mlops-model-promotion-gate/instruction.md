# MLOps — Production Model Promotion Gate

Implement `/app/promotion_gate.py`.

Invocation:

```bash
python /app/promotion_gate.py --candidate /app/data/candidate.json   --registry /app/data/registry.json --out /app/promotion.json
```

This is an offline model-registry policy engine.

## Candidate

The candidate contains:
- `model_name`
- `version`
- `stage`
- `artifact.path`
- `artifact.sha256`
- `training.dataset_id`
- `training.dataset_version`
- `training.code_commit`
- `evaluation.metrics`
- `evaluation.samples`
- `evaluation.reference`
- `approval.required`
- `approval.approved`

## Registry

Contains current production model, allowed stage transitions, metric policy, dataset policy,
and evaluation baselines.

## Promotion rules

A candidate may move only:

`dev -> staging -> production`

A direct `dev -> production` is forbidden.

Promotion to staging requires:
- artifact exists;
- SHA256 exactly matches the file;
- model name matches registry;
- version is semver-like and greater than the currently registered version for that stage;
- dataset is allowed and not marked revoked;
- code commit is non-empty;
- evaluation has all required metrics;
- minimum sample count is met.

Promotion to production additionally requires:
- candidate stage is `staging`;
- approval is required and `approved == true`;
- every production metric meets its absolute threshold;
- no metric regresses from the current production baseline by more than `max_regression`;
- safety metrics must not regress at all;
- evaluation dataset version must be at least the minimum approved version;
- artifact checksum must match the immutable registry entry.

## Metric semantics

For metrics marked `higher_is_better=true`, candidate >= threshold and
candidate >= baseline - max_regression.

For `higher_is_better=false`, candidate <= threshold and
candidate <= baseline + max_regression.

Do not trust candidate-supplied `passed`, `delta`, `improvement`, or `scorecard` fields.
Recompute decisions from raw metric values.

## Output

```json
{
  "decision":"promote|reject",
  "target_stage":"staging|production",
  "model_name":"...",
  "version":"...",
  "reasons":["..."]
}
```

Reasons must be deterministic and sorted.

Never output artifact contents or secrets.

## Hidden adversarial cases

- checksum mismatch;
- version downgrade;
- semver confusion (`1.10.0` vs `1.9.0`);
- missing metric;
- metric direction inversion;
- baseline regression hidden by a fake delta;
- revoked dataset;
- stale dataset;
- missing approval;
- safety metric regression;
- direct production promotion;
- candidate claiming a false `passed=true`;
- duplicate metric names;
- malformed JSON;
- large evaluation arrays;
- deterministic repeated invocation.
