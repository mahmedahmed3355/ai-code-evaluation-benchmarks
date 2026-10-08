from pathlib import Path
import os, json, yaml, subprocess, tempfile, shutil

D=Path(os.environ.get("TASK_DATA", "/app/data"))
def y(n): return yaml.safe_load((D/n).read_text())
def dep(): return y("deployment.yaml")
def api():
    return next(c for c in dep()["spec"]["template"]["spec"]["containers"] if c["name"]=="api")

def test_identity_is_coherent():
    d=dep(); s=y("service.yaml"); p=y("pdb.yaml")
    labels=d["spec"]["template"]["metadata"]["labels"]
    assert d["spec"]["selector"]["matchLabels"]==labels
    assert s["spec"]["selector"]==labels
    assert p["spec"]["selector"]["matchLabels"]==labels

def test_rollout_availability_contract():
    d=dep(); r=d["spec"]["strategy"]["rollingUpdate"]
    assert d["spec"]["replicas"]==3
    assert d["spec"]["minReadySeconds"]==10
    assert r=={"maxUnavailable":1,"maxSurge":1}

def test_service_traffic_contract():
    s=y("service.yaml")
    assert s["spec"]["ports"]==[{"name":"http","port":80,"targetPort":8080}]

def test_pdb_contract():
    p=y("pdb.yaml")
    assert p["spec"]["minAvailable"]==2

def test_runtime_contract():
    d=dep(); c=api()
    assert any(x["containerPort"]==8080 for x in c["ports"])
    assert c["readinessProbe"]["httpGet"]=={"path":"/health","port":8080}
    assert c["livenessProbe"]["httpGet"]=={"path":"/health","port":8080}
    assert c["env"][0]["valueFrom"]["configMapKeyRef"]["name"]=="inference-config"
    assert y("config.yaml")["data"]["PORT"]=="8080"

def test_security_and_resources_preserved():
    d=dep(); pod=d["spec"]["template"]["spec"]; c=api()
    assert pod["automountServiceAccountToken"] is False
    assert pod["securityContext"]["runAsNonRoot"] is True
    assert c["securityContext"]["readOnlyRootFilesystem"] is True
    assert c["resources"]["requests"]=={"cpu":"100m","memory":"128Mi"}
    assert c["resources"]["limits"]=={"cpu":"500m","memory":"256Mi"}

def test_validator_passes():
    out=subprocess.run(["python3",os.environ.get("VALIDATOR","/app/validate.py")],capture_output=True,text=True)
    assert out.returncode==0, out.stdout+out.stderr
    assert "VALIDATION=PASS" in out.stdout

def test_no_broad_service_or_pdb_selector():
    s=y("service.yaml"); p=y("pdb.yaml")
    assert len(s["spec"]["selector"])==3
    assert len(p["spec"]["selector"]["matchLabels"])==3
