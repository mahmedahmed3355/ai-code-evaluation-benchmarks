import numpy as np
def _transform(s,n):
 if n=="log1p": return np.log1p(s.clip(lower=0))
 if n=="signed_log1p": return np.sign(s)*np.log1p(np.abs(s))
 if n=="sqrt": return np.sqrt(s.clip(lower=0))
 return s
def prepare_features(frame,schema,artifact,fit_on=None):
 cols=schema["features"]; work=frame.copy()
 for c in cols: work[c]=_transform(work[c].fillna(work[c].mean()),schema["transforms"][c])
 return work[cols],work[schema["target_column"]]
