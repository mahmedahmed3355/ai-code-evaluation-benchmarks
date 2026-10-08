import numpy as np

def sigmoid(z): return 1.0/(1.0+np.exp(-np.clip(z,-40,40)))
def loss(y,p):
    p=np.clip(p,1e-7,1-1e-7); return float(-np.mean(y*np.log(p)+(1-y)*np.log(1-p)))
def train(X,y,w,lr,epochs,checkpoint_every):
    beta=np.zeros(X.shape[1]); bias=0.0; cps=[]
    sw=np.where(y==1,w[1],w[0])
    for ep in range(1,epochs+1):
        p=sigmoid(X@beta+bias); err=(p-y)*sw; z=sw.mean()
        beta-=lr*(X.T@err)/(len(y)*z); bias-=lr*err.mean()/z
        if ep%checkpoint_every==0: cps.append((ep,beta.copy(),bias))
    return cps
def predict_logits(X,beta,bias): return X@beta+bias
