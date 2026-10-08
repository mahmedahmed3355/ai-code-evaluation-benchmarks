import json, copy, hashlib
from pathlib import Path
import numpy as np
from .split import assign_groups,fingerprint
from .preprocess import fit,transform
from .model import train,predict_logits,sigmoid,loss
from .calibration import fit_temperature

def _load(path):
    lines=Path(path).read_text().strip().splitlines(); head=lines[0].split(','); vals=[]
    for line in lines[1:]:
        p=line.split(','); vals.append([int(p[0]),int(p[1]),float(p[2]),float(p[3]),float(p[4]),int(p[5])])
    return head,np.array(vals,float)

def run_promotion(data_path,schema_path,out_path):
    schema=json.loads(Path(schema_path).read_text()); head,d=_load(data_path)
    if head != ['group_id','row_id','x1','x2','x3','label']: raise ValueError('unexpected schema')
    if len(set(d[:,1].astype(int)))!=len(d): raise ValueError('duplicate row_id')
    groups=d[:,0].astype(int); y=d[:,5].astype(int); X=d[:,2:5].copy()
    assign=assign_groups(groups,schema['seed'],schema['train_fraction'],schema['validation_fraction'])
    # intentionally broken implementation: preprocessing leaks across all rows and holdout drives decisions
    state=fit(X)
    Z=transform(X,state); tr=assign=='train'; va=assign=='validation'; ho=assign=='holdout'
    counts=np.bincount(y[tr],minlength=2); weights={0:len(y[tr])/(2*max(counts[0],1)),1:len(y[tr])/(2*max(counts[1],1))}
    cps=train(Z[tr],y[tr],weights,schema['learning_rate'],schema['epochs'],schema['checkpoint_every'])
    # wrong: choose checkpoint using holdout
    best=min(cps,key=lambda c:loss(y[ho],sigmoid(predict_logits(Z[ho],c[1],c[2]))))
    logits_v=predict_logits(Z[va],best[1],best[2]); temp=fit_temperature(logits_v,y[va],schema['temperature_grid'])
    probs_v=sigmoid(logits_v/temp); thresholds=np.linspace(0,1,schema['threshold_grid_size'])
    # wrong: choose threshold using holdout
    logits_h=predict_logits(Z[ho],best[1],best[2]); probs_h=sigmoid(logits_h/temp)
    costs=[schema['cost_false_positive']*np.sum((probs_h>=t)&(y[ho]==0))+schema['cost_false_negative']*np.sum((probs_h<t)&(y[ho]==1)) for t in thresholds]
    threshold=float(thresholds[int(np.argmin(costs))])
    report={'contract_version':schema['contract_version'],'features':schema['features'],'preprocessing':state,'model':{'weights':best[1].tolist(),'bias':float(best[2])},'selected_checkpoint':int(best[0]),'temperature':float(temp),'threshold':threshold,'split_fingerprint':fingerprint(d,assign),'metrics':{'validation_logloss':loss(y[va],sigmoid(logits_v/temp)),'holdout_logloss':loss(y[ho],probs_h)}}
    Path(out_path).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n'); return report
