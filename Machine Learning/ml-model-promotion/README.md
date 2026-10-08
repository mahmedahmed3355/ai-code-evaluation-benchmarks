# ML Model Promotion Gate — `ml-model-promotion-017`

## Overview

This task simulates a production ML release gate for a binary classification model. A training pipeline produces a candidate model, evaluates it against a frozen validation/test protocol, chooses an operating threshold, and emits a promotion artifact.

The repository contains a deliberately inconsistent implementation. The agent must repair the pipeline so that **model selection, preprocessing, calibration, threshold selection, and promotion decisions all obey the persisted experiment contract**.

This is intentionally not a toy "fit a classifier" exercise. The difficult part is reconstructing the intended ML lifecycle from several interacting artifacts and preserving the statistical boundaries between training, validation, and final holdout data.

## What makes it difficult

The failure modes cross multiple layers:

- group-aware splitting must prevent customer/entity leakage;
- preprocessing statistics must be fitted only on the training partition;
- class weights must be derived from training labels only;
- candidate checkpoints must be selected by validation objective, not test performance;
- probability calibration is fitted on validation predictions and must not mutate the base model;
- the operating threshold is selected from validation data using an explicit cost matrix;
- the frozen holdout may only be used once for the final report;
- promotion requires all artifact fields to agree with the actual model state;
- repeated evaluation must be deterministic and must not mutate the artifact;
- corrupted/incompatible artifacts must fail closed.

## Expected behavior

The repaired pipeline must:

1. load the schema and dataset;
2. create deterministic group-disjoint train/validation/holdout partitions;
3. fit preprocessing on train only;
4. train the candidate logistic model with train-derived class weights;
5. choose the checkpoint using validation log-loss;
6. fit a temperature calibrator on validation logits without changing model weights;
7. select the decision threshold on validation data according to the supplied false-positive/false-negative costs;
8. evaluate the frozen holdout exactly once for the final promotion report;
9. emit a self-consistent JSON artifact containing model, preprocessing, calibration, threshold, split fingerprints, and metrics;
10. refuse promotion if any contract invariant is violated.

## Constraints

- CPU only.
- Python standard library + NumPy only.
- No network access.
- Do not hard-code fixture values or expected metrics.
- Do not bypass the pipeline by returning precomputed scores.
- Do not modify tests or verifier files.
- The solution must work with alternate valid datasets/artifacts supplied by the verifier.

## Validation philosophy

The verifier checks the **behavioral contract**, not merely whether the visible fixture produces a good score. Hidden checks change group IDs, class imbalance, feature scale, row ordering, and calibration conditions. A solution that leaks holdout information or hard-codes the supplied data should fail.

## Directory layout

```text
environment/   broken runtime and deterministic fixtures
solution/      reference repair
 tests/         candidate-facing and independent verification
```

## Success criteria

The candidate must produce a promotion artifact that is statistically valid, reproducible, internally consistent, and generated without using the final holdout to make training or selection decisions.
