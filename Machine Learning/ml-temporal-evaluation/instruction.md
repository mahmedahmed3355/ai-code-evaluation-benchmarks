# Task: Restore a leakage-safe temporal ML evaluation service

Repair `/app/ml_eval` without changing `ml_eval.pipeline.evaluate`'s public API.

Requirements:
1. Split by `schema.json`: train `timestamp <= train_end`; validation `train_end < timestamp <= validation_end`; future rows must not affect the validation metric.
2. Never fit preprocessing during evaluation; use persisted imputation/scaling from `model_artifact.json`.
3. Respect schema/artifact feature order; exclude `target` and `event_id`.
4. Reject duplicate `event_id` values.
5. Apply transforms, scaling, weights, bias, and calibration according to the persisted contract.
6. Return `auc`, `train_rows`, `validation_rows`, `future_rows_ignored`, `feature_names`.
7. Do not mutate input or artifact; repeated calls must be identical.
8. No retraining, network, fixture-specific hard-coding, or API changes.

The verifier covers reordered columns, missing values, distribution shift, future contamination, boundary timestamps, duplicates, alternate artifacts, immutability, and re-entrancy.
