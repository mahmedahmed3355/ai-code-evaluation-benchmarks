# Repair the ML Model Promotion Pipeline

You are repairing a production-style binary classification release gate.

The implementation under `environment/ml_promo/` is intentionally broken. Restore the intended behavior without changing the public API of the package.

## Contract

The pipeline must satisfy all of the following:

### 1. Split integrity
- Partition rows into train, validation, and final holdout using the `group_id` column.
- A group must belong to exactly one partition.
- The split must be deterministic for a fixed seed.
- Row order must not affect the assignment.

### 2. Preprocessing integrity
- Numeric means/scales are fitted from **train rows only**.
- Constant columns must receive a stable non-zero scale.
- Missing numeric values are imputed using train statistics.
- The persisted preprocessing state must be sufficient to reproduce inference.

### 3. Training integrity
- Train the provided logistic model using only the training partition.
- Derive class weights from training labels only.
- Keep model weights separate from calibration parameters.
- Checkpoint selection uses validation log-loss only.
- The final holdout must never participate in checkpoint selection.

### 4. Calibration and thresholding
- Fit scalar temperature calibration on validation logits only.
- Temperature must remain positive.
- Select the classification threshold on validation probabilities using the cost matrix in `schema.json`.
- Do not optimize the threshold on holdout labels.

### 5. Promotion artifact
The artifact must contain the actual:
- split fingerprints;
- feature order;
- preprocessing statistics;
- model weights/bias;
- selected checkpoint index;
- calibration temperature;
- operating threshold;
- validation metrics;
- final holdout metrics;
- contract version.

### 6. Holdout rule
The holdout is a final audit set. It may be scored for the final report, but its labels must not influence preprocessing, training, checkpoint selection, calibration, threshold selection, or promotion criteria.

### 7. Safety
- Evaluation must be re-entrant and deterministic.
- Input data and persisted artifacts must not be mutated.
- Invalid schema/artifact combinations must fail closed with a clear exception.

Do not retrain with a different model, remove the holdout, weaken checks, or special-case the supplied fixtures. Fix the pipeline itself.
