import numpy as np
from .contract import load_schema,validate_artifact
from .features import iter_chunks
from .preprocessing import load_artifact,transform
from .model import predict_proba
def predict_file(path,artifact_path="/app/data/model_artifact.json"):
    schema=load_schema(); a=load_artifact(artifact_path); validate_artifact(a,schema)
    out=[]
    for x,_ in iter_chunks(path,schema,chunk_size=64):
        out.extend(predict_proba(transform(x,a),a).tolist())
    return np.asarray(out,float)
