import csv, json, shutil, tempfile
from pathlib import Path
import numpy as np
from ml_promo.pipeline import run_promotion
ROOT=Path('/app'); base=ROOT/'data/events.csv'; schema=json.loads((ROOT/'data/schema.json').read_text())
# 1. permutation invariance
lines=base.read_text().splitlines(); head,body=lines[0],lines[1:]; perm=list(reversed(body)); d=ROOT/'data/perm.csv'; d.write_text(head+'\n'+'\n'.join(perm)+'\n')
baseline=run_promotion(str(base),str(ROOT/'data/schema.json'),'/tmp/a.json'); b=run_promotion(str(d),str(ROOT/'data/schema.json'),'/tmp/b.json'); assert baseline['split_fingerprint']==b['split_fingerprint']; assert baseline['model']==b['model']
# 2. group leakage canary: duplicate one group with a distinct row should remain same partition
# 3. NaN injection: must use train-only stats and remain finite
raw=list(csv.DictReader(base.open())); raw[0]['x1']=''
n=ROOT/'data/nan.csv'; fields=raw[0].keys();
with n.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(raw)
r=run_promotion(str(n),str(ROOT/'data/schema.json'),'/tmp/nan.json'); assert np.isfinite(r['preprocessing']['mean']).all()
# 4. invalid duplicate id must fail closed
raw=list(csv.DictReader(base.open())); raw[1]['row_id']=raw[0]['row_id']; bad=ROOT/'data/dup.csv'
with bad.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(raw)
try: run_promotion(str(bad),str(ROOT/'data/schema.json'),'/tmp/bad.json'); raise AssertionError('duplicate accepted')
except ValueError: pass
# 5. altered holdout labels must not change model selection/preprocessing/threshold
raw=list(csv.DictReader(base.open())); assign=[]
from ml_promo.split import assign_groups
g=np.array([int(x['group_id']) for x in raw]); asg=assign_groups(g,schema['seed'],schema['train_fraction'],schema['validation_fraction'])
for i,a in enumerate(asg):
 if a=='holdout': raw[i]['label']=str(1-int(raw[i]['label']))
q=ROOT/'data/holdout_flip.csv'
with q.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(raw)
c=run_promotion(str(q),str(ROOT/'data/schema.json'),'/tmp/c.json'); assert baseline['model']==c['model'] and baseline['threshold']==c['threshold'] and baseline['temperature']==c['temperature']
print('HIDDEN PASS')
