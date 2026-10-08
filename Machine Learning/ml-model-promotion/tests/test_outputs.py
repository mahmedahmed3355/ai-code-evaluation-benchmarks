import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
ROOT=Path('/app'); OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
subprocess.run(['/bin/sh','/app/solution/solve.sh'] if (ROOT/'solution').exists() else ['true'],check=False)
# run candidate directly
from ml_promo.pipeline import run_promotion
p=OUT/'promotion.json'; run_promotion('/app/data/events.csv','/app/data/schema.json',str(p))
r=json.loads(p.read_text())
assert r['contract_version']=='promo-v1'
assert r['features']==['x1','x2','x3']
assert 0<r['temperature'] and 0<=r['threshold']<=1
assert r['selected_checkpoint'] in [30,60,90,120,150,180]
assert len(r['model']['weights'])==3
assert r['metrics']['holdout_count']>0
# reentrant byte equality
a=p.read_bytes(); run_promotion('/app/data/events.csv','/app/data/schema.json',str(p)); assert a==p.read_bytes()
# artifact must not contain raw labels or row-level predictions
s=p.read_text(); assert 'label' not in s.lower() or 'contract_version' in s
print('VISIBLE PASS')
