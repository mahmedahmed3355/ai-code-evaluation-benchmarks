#!/bin/sh
set -eu
python -m compileall -q /app/app
rm -rf /tmp/validation-run
python -m app.run --outdir /tmp/validation-run
python - <<'PY'
import json, torch
from app.reference import reference_state
cfg=json.load(open('/app/data/config.json'))
ref, opt, steps=reference_state(cfg['seed'],cfg)
run=torch.load('/tmp/validation-run/final.pt',map_location='cpu',weights_only=False)
maxdiff=max((ref[k]-run['model'][k]).abs().max().item() for k in ref)
print('validation_max_parameter_diff=',maxdiff)
print('validation_global_step=',run['global_step'])
if run['global_step'] != steps or maxdiff >= 1e-7:
    raise SystemExit('distributed training result does not match reference')
print('VALIDATION=PASS')
PY
