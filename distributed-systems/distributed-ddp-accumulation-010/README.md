# distributed-ddp-accumulation-010

## Distributed Training Correctness Incident

This benchmark reproduces a realistic PyTorch DDP migration failure in a small CPU training service. The trainer uses two distributed ranks, sharded data, gradient accumulation, and checkpoint/resume. The visible symptom is validation drift when the number of samples contributing to an optimizer update is not the same as the configured accumulation capacity.

The difficult part is not changing a divisor. The implementation must preserve the semantics of a **global, sample-weighted optimizer update** while respecting DDP's collective execution rules. A correct repair also has to keep optimizer-step numbering and checkpoint/resume behavior deterministic.

## Failure model

The intentionally broken trainer:

- treats local accumulation as if every rank contributed the same sample count;
- uses DDP's normal gradient averaging without accounting for the desired global sample weighting;
- assumes the default shard shape is representative of every accumulation window;
- derives the rendezvous port from Python's randomized `hash()` value, which can give spawned ranks different endpoints;
- must remain compatible with checkpoint/resume semantics.

The production-style fix is expected to reason about **global sample counts, collective synchronization, uneven local work, and optimizer-update boundaries** rather than hardcoding the provided output.

## Environment

- Python 3
- PyTorch CPU
- `torch.distributed` / Gloo
- two ranks
- deterministic synthetic classification data
- no network access

## Repository contract

```text
environment/app/model.py       model definition
environment/app/trainer.py     code under repair
environment/app/run.py         CLI runner
environment/app/reference.py   independent reference calculation
environment/data/config.json   training contract
environment/data/dataset.json  deterministic sharded data
solution/solve.sh              oracle/reference repair
tests/test_outputs.py          visible verifier tests
tests/hidden_tests.py          adversarial checks
```

## Acceptance criteria

A correct implementation must:

1. match the independent single-process reference for the default workload;
2. remain correct when `accumulation_steps` changes and the final window is partial;
3. remain correct when rank shards have unequal lengths;
4. keep real multi-process DDP participation;
5. avoid mismatched collective sequences when ranks process different numbers of local samples;
6. preserve the checkpoint contract and make resumed training bitwise-equivalent within the verifier tolerance to uninterrupted training;
7. keep `global_step` tied to optimizer updates;
8. avoid modifying the model, dataset, reference implementation, or verifier to hide the defect.

Run the repaired environment with:

```bash
/app/validate.sh
```

## Why this is difficult

The task combines several constraints that interact in real distributed training systems: DDP gradient semantics, sample weighting, uneven work per rank, collective ordering, deterministic rendezvous, and checkpoint state. A locally plausible repair can still deadlock, silently change the effective learning rate, or pass the default case while failing on a different shard/window shape.

## Verification philosophy

The verifier compares behavior against an independent reference and exercises alternate accumulation settings and uneven shards. Source checks are limited to architectural invariants; correctness is primarily established through executed training results.

## Author

Forge Bench / Mohamed Ahmed
