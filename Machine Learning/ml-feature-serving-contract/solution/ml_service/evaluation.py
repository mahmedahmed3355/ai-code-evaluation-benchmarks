import numpy as np
from .contract import load_schema,validate_artifact
from .features import iter_chunks
from .preprocessing import transform
from .model import predict_proba
def auc(y,s):
    order=np.argsort(s,kind="mergesort"); ss=s[order]; ranks=np.empty(len(s),float); i=0
    while i<len(s):
        j=i+1
        while j<len(s) and ss[j]==ss[i]: j+=1
        ranks[order[i:j]]=(i+j+1)/2; i=j
    pos=np.sum(y==1); neg=np.sum(y==0)
    if pos==0 or neg==0: raise ValueError("both classes required")
    return float((ranks[y==1].sum()-pos*(pos+1)/2)/(pos*neg))
def evaluate(path,a):
    s=load_schema(); validate_artifact(a,s); xs=[]; ys=[]
    for x,y in iter_chunks(path,s,chunk_size=64,require_target=True):
        xs.append(predict_proba(transform(x,a),a)); ys.append(y)
    return auc(np.concatenate(ys),np.concatenate(xs))
