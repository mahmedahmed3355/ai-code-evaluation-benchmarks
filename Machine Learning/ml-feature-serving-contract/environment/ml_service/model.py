import numpy as np
def predict_proba(x,a):
    raw=np.c_[np.ones(len(x)),x]@np.asarray(a["weights"])
    # BUG: calibration bias is applied before temperature.
    z=(raw+float(a["calibration"]["bias"]))/float(a["calibration"]["temperature"])
    return 1/(1+np.exp(-np.clip(z,-60,60)))
