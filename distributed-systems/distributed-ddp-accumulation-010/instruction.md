# Repair the Distributed Training Incident

A two-rank PyTorch training service was migrated to DDP and now produces incorrect validation results. The failure becomes visible when an optimizer update contains a different number of samples than the nominal accumulation capacity. The same trainer must also support deterministic checkpoint/resume.

Repair **only** `environment/app/trainer.py` unless a runtime configuration change is strictly required to make the existing distributed contract deterministic. Do not modify the model, dataset, reference implementation, tests, verifier, or output format.

## Required behavior

1. Preserve the public `train(config=None, outdir=..., resume=None, stop_after=None)` API.
2. Keep two-process CPU DDP using Gloo.
3. Each optimizer update must equal the sample-weighted update of the independent reference: every contributing sample has equal weight, regardless of local shard size or accumulation-window size.
4. All ranks must participate in the same distributed collective sequence. Uneven local sample counts must not cause a deadlock.
5. DDP must remain genuinely distributed. Do not replace it with a single process, remove the process group, or serialize training with a barrier for every sample.
6. `global_step` counts optimizer updates only.
7. Checkpoint/resume must preserve the optimizer-update sequence. A run stopped after one optimizer update and resumed from its checkpoint must match an uninterrupted run.
8. Keep the existing checkpoint keys and artifact paths.
9. Do not hardcode reference weights, expected outputs, or a special-case answer for the provided configuration.
10. Keep the implementation deterministic.

## Important edge cases

The verifier may change:

- random seed;
- learning rate;
- accumulation steps;
- number of optimizer updates;
- relative shard lengths;
- partial final accumulation windows.

A correct solution must handle those cases from the configuration and data rather than from fixed constants.

## What not to change

Do not edit:

- `environment/app/model.py`
- `environment/app/reference.py`
- `environment/data/dataset.json`
- `environment/data/config.json` except for a deterministic rendezvous setting if needed
- `tests/*`
- `solution/*`

Do not weaken numerical tolerances or bypass verification.

## Validation

After the repair, run:

```bash
/app/validate.sh
```

The final implementation must match the independent reference and remain correct under the hidden adversarial cases.
