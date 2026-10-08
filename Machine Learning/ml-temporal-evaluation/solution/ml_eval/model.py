import numpy as np
def predict_proba(X,a):
 m=np.array([a["scale_mean"][c] for c in a["feature_order"]],float); sd=np.array([a["scale_std"][c] for c in a["feature_order"]],float); z=((np.asarray(X,float)-m)/sd)@np.array(a["weights"],float)+float(a["bias"]); c=a["calibration"]; z=z/float(c["temperature"])+float(c["bias"]); return 1/(1+np.exp(-np.clip(z,-60,60)))
