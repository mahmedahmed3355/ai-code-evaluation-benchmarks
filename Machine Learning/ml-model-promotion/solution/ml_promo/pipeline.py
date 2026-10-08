import json
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
    expected=['group_id','row_id']+schema['features']+[schema['target']]
    if head != expected: raise ValueError('unexpected schema')
    if len(set(d[:,1].astype(int)))!=len(d): raise ValueError('duplicate row_id')
    groups=d[:,0].astype(int); y=d[:,-1].astype(int); X=d[:,2:-1].copy()
    if not np.isin(y,[0,1]).all(): raise ValueError('target must be binary')
    assign=assign_groups(groups,schema['seed'],schema['train_fraction'],schema['validation_fraction'])
    tr=assign=='train'; va=assign=='validation'; ho=assign=='holdout'
    state=fit(X[tr]); Ztr=transform(X[tr],state); Zva=transform(X[va],state); Zho=transform(X[ho],state)
    counts=np.bincount(y[tr],minlength=2)
    weights={0:len(y[tr])/(2*max(counts[0],1)),1:len(y[tr])/(2*max(counts[1],1))}
    cps=train(Ztr,y[tr],weights,schema['learning_rate'],schema['epochs'],schema['checkpoint_every'])
    best=min(cps,key=lambda c:(loss(y[va],sigmoid(predict_logits(Zva,c[1],c[2]))),c[0]))
    logits_v=predict_logits(Zva,best[1],best[2]); temp=fit_temperature(logits_v,y[va],schema['temperature_grid'])
    probs_v=sigmoid(logits_v/temp); thresholds=np.linspace(0,1,schema['threshold_grid_size'])
    fp=schema['cost_false_positive']; fn=schema['cost_false_negative']
    costs=[fp*np.sum((probs_v>=t)&(y[va]==0))+fn*np.sum((probs_v<t)&(y[va]==1)) for t in thresholds]
    threshold=float(thresholds[int(np.argmin(costs))])
    logits_h=predict_logits(Zho,best[1],best[2]); probs_h=sigmoid(logits_h/temp)
    val_loss=loss(y[va],probs_v); hold_loss=loss(y[ho],probs_h)
    report={'contract_version':schema['contract_version'],'features':schema['features'],'preprocessing':state,'model':{'weights':best[1].tolist(),'bias':float(best[2])},'selected_checkpoint':int(best[0]),'temperature':float(temp),'threshold':threshold,'split_fingerprint':fingerprint(d,assign),'metrics':{'validation_logloss':val_loss,'holdout_logloss':hold_loss,'validation_cost':float(min(costs)),'holdout_count':int(ho.sum())}}
    Path(out_path).write_text(json.dumps(report,sort_keys=True,indent=2)+'\n'); return report
