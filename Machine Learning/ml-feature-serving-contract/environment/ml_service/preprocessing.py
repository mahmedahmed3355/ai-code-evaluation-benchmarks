import json,copy
from pathlib import Path
import numpy as np
from .contract import load_schema,validate_artifact
def load_artifact(path="/app/data/model_artifact.json"):
    a=json.loads(Path(path).read_text()); validate_artifact(a,load_schema()); return a
def transform(x,a):
    pp=a["preprocessing"]; x=np.nan_to_num(np.asarray(x,float),nan=0.0)
    x=np.clip(x,np.asarray(pp["clip_low"]),np.asarray(pp["clip_high"]))
    return (x-np.asarray(pp["scale_mean"]))/np.asarray(pp["scale_std"])
