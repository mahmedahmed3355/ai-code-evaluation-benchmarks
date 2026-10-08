import numpy as np
def predict_proba(x,a):
    w=np.asarray(a["weights"],float); raw=np.c_[np.ones(len(x)),x]@w
    cal=a["calibration"]; z=np.clip(raw/float(cal["temperature"])+float(cal["bias"]),-60,60)
    return 1/(1+np.exp(-z))
