import json, sys
from pathlib import Path
import numpy as np

APP=Path("/app")
DATA=APP/"data"
# Independent contract checks intentionally do not import candidate inference code.
schema=json.loads((DATA/"schema.json").read_text())
artifact=json.loads((DATA/"model_artifact.json").read_text())

checks={
 "schema_version": schema.get("version")=="1.0",
 "feature_order": artifact.get("feature_schema")==schema.get("features"),
 "weight_dimension": len(artifact.get("weights",[]))==len(schema.get("features",[]))+1,
 "calibration": float(artifact.get("calibration",{}).get("temperature",0))>0,
 "provenance": isinstance(artifact.get("fit_source"),str) and bool(artifact.get("fit_source")),
 "preprocess_lengths": all(len(artifact["preprocessing"][k])==len(schema["features"]) for k in ["impute_mean","transform","clip_low","clip_high","scale_mean","scale_std"]),
}
for k,v in checks.items(): print(f"{k}={'PASS' if v else 'FAIL'}")
if not all(checks.values()):
    print("VERIFIER=FAIL"); sys.exit(1)
print("VERIFIER=PASS")
