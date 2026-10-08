# ml-feature-serving-contract-015

## Incident

A binary-risk model was moved from an offline training pipeline into a batch inference service. Predictions looked plausible on ordinary rows, but production monitoring found that predictions changed when upstream systems reordered columns or emitted missing values.

The incident is a training/serving contract failure, not a model-quality problem.

The persisted model artifact contains the exact feature order, imputation statistics, transforms, clipping bounds, scaling statistics, model weights, and calibration parameters used by the reference pipeline.

The inference service must treat that artifact as the source of truth.

## Failure modes

The broken implementation contains several realistic integration defects:

- it relies on incoming CSV column order instead of the persisted feature schema;
- it applies missing-value handling inconsistently with the training artifact;
- it can apply transforms in the wrong stage;
- it uses a calibration formula that is not the artifact contract;
- it can mutate shared artifact state during repeated evaluation;
- it does not preserve stable row ordering across chunked inference;
- malformed artifacts are not always rejected before prediction.

These failures interact. Fixing one visible symptom is not enough.

## Contract

For every valid input:

1. Feature selection follows `artifact.feature_schema`, not input order.
2. Missing values use persisted `impute_mean`.
3. Each feature uses its persisted transform.
4. Clipping uses persisted post-transform bounds.
5. Scaling uses persisted `scale_mean` and `scale_std`.
6. The model uses the persisted intercept and weights.
7. Calibration uses `raw / temperature + bias`.
8. Predictions are finite probabilities in input-row order.
9. The artifact is immutable during inference and evaluation.
10. Invalid schema/artifact contracts fail closed.

The evaluator also uses generated inputs with reordered columns, missing values, distribution shift, duplicates, and target columns in different positions.

## Difficulty

This is intentionally an ML engineering task rather than a toy classifier exercise. The challenge is reconstructing the data/model contract from multiple artifacts and preserving it across inference, evaluation, repeated calls, and alternate inputs.

No network or GPU is required.
