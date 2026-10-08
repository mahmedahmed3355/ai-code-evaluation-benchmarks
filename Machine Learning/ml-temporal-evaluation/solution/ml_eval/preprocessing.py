import numpy as np
def _transform(s,n):
 if n=="log1p": return np.log1p(s.clip(lower=0))
 if n=="signed_log1p": return np.sign(s)*np.log1p(np.abs(s))
 if n=="sqrt": return np.sqrt(s.clip(lower=0))
 raise ValueError("unknown transform")
def prepare_features(frame,schema,artifact):
 cols=list(artifact["feature_order"])
 if cols!=list(schema["features"]): raise ValueError("schema/artifact feature order mismatch")
 w=frame.copy(deep=True)
 for c in cols: w[c]=_transform(w[c].fillna(artifact["imputation"][c]),schema["transforms"][c])
 return w[cols],w[schema["target_column"]].astype(int)
