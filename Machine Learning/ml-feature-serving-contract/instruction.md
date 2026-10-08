# Task: Restore the training/serving feature contract

A binary-risk model is producing inconsistent batch predictions after being moved into a serving pipeline.

Diagnose and repair the ML inference stack so it follows the persisted model artifact and schema exactly.

## Required behavior

- The persisted artifact is authoritative for feature order and preprocessing.
- Input CSV column order must not affect predictions.
- Missing values must use the artifact's persisted imputation statistics.
- Apply each persisted feature transform before clipping and scaling.
- Preserve the artifact's model weights and intercept.
- Apply calibration as `raw / temperature + bias`.
- Preserve input row order, including duplicate rows.
- Inference and evaluation must be re-entrant and must not mutate the loaded artifact.
- Evaluation must use the schema's target field rather than assuming a fixed CSV position/name.
- Invalid artifact/schema contracts must fail closed.
- Alternate artifact paths must work.
- Large inputs must remain bounded by chunked ingestion.

## Constraints

Do not modify:

- `data/model_artifact.json`
- `data/schema.json`
- `tests/`
- the reference implementation.

Do not:

- hard-code expected predictions;
- train a new model;
- infer feature order from the current CSV;
- silently replace invalid artifact fields;
- mutate the persisted artifact;
- special-case the supplied fixtures.

Run:

```bash
python -m ml_service /app/data/nominal.csv
```

and use the supplied validation suite before finishing.
