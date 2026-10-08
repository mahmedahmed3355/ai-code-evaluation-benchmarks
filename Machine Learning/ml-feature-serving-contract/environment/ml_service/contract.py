import json
from pathlib import Path
import numpy as np
def load_schema(path="/app/data/schema.json"):
    s=json.loads(Path(path).read_text())
    if s.get("version")!="1.0" or not isinstance(s.get("features"),list) or len(s["features"])!=6:
        raise ValueError("invalid schema")
    if len(set(s["features"]))!=6 or s.get("target") not in {"target","label"}:
        raise ValueError("invalid schema")
    return s
def validate_artifact(a,schema):
    if a.get("version")!="1.0" or a.get("feature_schema")!=schema["features"]:
        raise ValueError("artifact/schema feature contract mismatch")
    pp=a.get("preprocessing",{})
    n=len(schema["features"])
    for k in ("impute_mean","transform","clip_low","clip_high","scale_mean","scale_std"):
        if k not in pp or len(pp[k])!=n: raise ValueError("invalid preprocessing contract")
    if len(a.get("weights",[]))!=n+1: raise ValueError("invalid weights")
    if pp["transform"] and any(t not in {"identity","log1p","signed_log1p"} for t in pp["transform"]):
        raise ValueError("invalid transform")
    if any(float(x)<=0 for x in pp["scale_std"]): raise ValueError("invalid scale std")
    if any(float(x)>=float(y) for x,y in zip(pp["clip_low"],pp["clip_high"])): raise ValueError("invalid clip bounds")
    cal=a.get("calibration",{})
    if float(cal.get("temperature",0))<=0: raise ValueError("invalid calibration")
    if not isinstance(a.get("fit_source"),str) or not a["fit_source"]: raise ValueError("invalid provenance")
    nums=pp["impute_mean"]+pp["clip_low"]+pp["clip_high"]+pp["scale_mean"]+pp["scale_std"]+a["weights"]+[cal["temperature"],cal["bias"]]
    if not all(np.isfinite(float(x)) for x in nums): raise ValueError("non-finite artifact")
    return a
