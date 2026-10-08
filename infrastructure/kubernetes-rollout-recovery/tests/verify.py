#!/usr/bin/env python3
import os
from pathlib import Path
import yaml

D=Path(os.environ.get("TASK_DATA","/app/data"))
files={n: yaml.safe_load((D/n).read_text()) for n in
       ["deployment.yaml","service.yaml","pdb.yaml","config.yaml"]}
d,s,p,c=files.values()
labels=d["spec"]["template"]["metadata"]["labels"]
checks=[
    d["spec"]["selector"]["matchLabels"]==labels,
    s["spec"]["selector"]==labels,
    p["spec"]["selector"]["matchLabels"]==labels,
    d["spec"]["replicas"]==3,
    d["spec"]["strategy"]["rollingUpdate"]=={"maxUnavailable":1,"maxSurge":1},
    d["spec"]["minReadySeconds"]==10,
    s["spec"]["ports"][0]["targetPort"]==8080,
    p["spec"]["minAvailable"]==2,
    c["data"]["PORT"]=="8080",
]
if not all(checks):
    raise SystemExit("VERIFIER=FAIL")
print("VERIFIER=PASS")
