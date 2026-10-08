import json
from pathlib import Path
import yaml

D=Path("/app/data")
def y(n): return yaml.safe_load((D/n).read_text())
def labels(x): return x.get("matchLabels", x.get("selector", {}))

dep=y("deployment.yaml"); svc=y("service.yaml"); pdb=y("pdb.yaml"); cfg=y("config.yaml")
exp=json.loads((D/"expected_state.json").read_text())
want=exp["identity"]

assert dep["kind"]=="Deployment" and dep["metadata"]["name"]=="inference-api"
assert dep["spec"]["replicas"]==3
assert dep["spec"]["minReadySeconds"]==10
ru=dep["spec"]["strategy"]["rollingUpdate"]
assert dep["spec"]["strategy"]["type"]=="RollingUpdate" and ru=={"maxUnavailable":1,"maxSurge":1}

pod=dep["spec"]["template"]; pl=pod["metadata"]["labels"]
sel=dep["spec"]["selector"]["matchLabels"]
assert sel==pl==want

assert svc["kind"]=="Service" and svc["metadata"]["name"]=="inference-api"
assert svc["spec"]["selector"]==want
port=svc["spec"]["ports"][0]
assert port["port"]==80 and port["targetPort"]==8080

assert pdb["kind"]=="PodDisruptionBudget" and pdb["metadata"]["name"]=="inference-api"
assert pdb["spec"]["minAvailable"]==2 and pdb["spec"]["selector"]["matchLabels"]==want

c=next(x for x in pod["spec"]["containers"] if x["name"]=="api")
assert any(p["containerPort"]==8080 for p in c["ports"])
for k in ("readinessProbe","livenessProbe"):
    assert c[k]["httpGet"]["path"]=="/health"
    assert c[k]["httpGet"]["port"]==8080
assert c["env"][0]["valueFrom"]["configMapKeyRef"]=={"name":"inference-config","key":"PORT"}
assert cfg["data"]["PORT"]=="8080"

assert pod["spec"]["automountServiceAccountToken"] is False
sc=pod["spec"]["securityContext"]
assert sc["runAsNonRoot"] is True and sc["runAsUser"]==10001 and sc["runAsGroup"]==10001
assert c["securityContext"]["readOnlyRootFilesystem"] is True
assert c["securityContext"]["allowPrivilegeEscalation"] is False
assert c["resources"]["requests"]=={"cpu":"100m","memory":"128Mi"}
assert c["resources"]["limits"]=={"cpu":"500m","memory":"256Mi"}

print("VALIDATION=PASS")
