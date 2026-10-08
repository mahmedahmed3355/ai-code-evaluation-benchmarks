import numpy as np

def fit(X):
    mean=np.nanmean(X,axis=0); scale=np.nanstd(X,axis=0); scale=np.where(scale<1e-8,1.0,scale)
    return {'mean':mean.tolist(),'scale':scale.tolist()}

def transform(X,state):
    mean=np.asarray(state['mean'],float); scale=np.asarray(state['scale'],float)
    if X.shape[1]!=len(mean): raise ValueError('feature dimension mismatch')
    X=np.asarray(X,float).copy(); inds=np.where(np.isnan(X)); X[inds]=mean[inds[1]]
    return (X-mean)/scale
