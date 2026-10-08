import copy,json
from pathlib import Path
import numpy as np
from .contract import load_schema,validate_artifact
_CACHE={}
def load_artifact(path="/app/data/model_artifact.json"):
    p=Path(path); raw=p.read_bytes(); key=str(p.resolve()); fp=(p.stat().st_size,p.stat().st_mtime_ns)
    if key in _CACHE and _CACHE[key][0]==fp: return copy.deepcopy(_CACHE[key][1])
    a=json.loads(raw.decode()); validate_artifact(a,load_schema())
    _CACHE[key]=(fp,copy.deepcopy(a)); return copy.deepcopy(a)
def transform(x,a):
    x=np.asarray(x,float); pp=a["preprocessing"]
    imp=np.asarray(pp["impute_mean"],float); lo=np.asarray(pp["clip_low"],float); hi=np.asarray(pp["clip_high"],float)
    mean=np.asarray(pp["scale_mean"],float); std=np.asarray(pp["scale_std"],float)
    out=np.where(np.isnan(x),imp,x).copy()
    for j,k in enumerate(pp["transform"]):
        if k=="log1p": out[:,j]=np.log1p(out[:,j])
        elif k=="signed_log1p": out[:,j]=np.sign(out[:,j])*np.log1p(np.abs(out[:,j]))
    out=np.clip(out,lo,hi)
    return (out-mean)/std
