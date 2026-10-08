import numpy as np
def predict_proba(X,a):
 m=np.array([a["scale_mean"][c] for c in a["feature_order"]]); sd=np.array([a["scale_std"][c] for c in a["feature_order"]]); x=(np.asarray(X)-m)/sd
 z=x@np.array(a["weights"])+a["bias"]; c=a["calibration"]; z=(z+c["bias"])*c["temperature"]; return 1/(1+np.exp(-z))
