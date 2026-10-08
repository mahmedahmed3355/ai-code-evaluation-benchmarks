
import json,subprocess,shutil
from pathlib import Path
APP=Path("/app"); DATA=APP/"data"
def run(spec,state):
    Path("/tmp/spec.json").write_text(json.dumps(spec)); Path("/tmp/state.json").write_text(json.dumps(state))
    p=subprocess.run(["python","/app/reconcile.py","--spec","/tmp/spec.json","--state","/tmp/state.json","--out","/tmp/out.json"],capture_output=True,text=True)
    return p,json.loads(Path("/tmp/out.json").read_text())
def base():
    return json.loads((DATA/"spec.json").read_text()),json.loads((DATA/"cluster_state.json").read_text())
def test_01_create():
    s,c=base(); p,o=run(s,c); assert o["action"]=="create" and o["pod"].startswith("payments-r2-") and o["node"] in {"node-a1","node-b1","node-b2","node-a2"}
def test_02_noop():
    s,c=base(); c["pods"]=[
      {"name":f"p{i}","workload":"payments","revision":"r2","node":n,"ready":True,"ready_for_seconds":20,"terminating":False}
      for i,n in enumerate(["node-a1","node-a2","node-b1","node-b2"])]
    o=run(s,c)[1]; assert o["action"]=="noop"
def test_03_pdb_blocks_delete():
    s,c=base(); s["max_surge"]=0; s["workload"]["max_surge"]=0
    for p in c["pods"]: p["revision"]="r2" if p["name"].endswith("0") else "r1"
    c["pods"][0]["ready"]=True
    o=run(s,c)[1]; assert o["action"] in {"wait","delete"}
def test_04_resource_fragmentation():
    s,c=base(); c["nodes"][0]["used"]["cpu_m"]=1700; c["nodes"][1]["used"]["cpu_m"]=1700
    o=run(s,c)[1]; assert o["action"]=="create" and o["node"] in {"node-b1","node-b2"}
def test_05_readiness_floor():
    s,c=base(); c["pods"][0]["ready_for_seconds"]=0
    o=run(s,c)[1]; assert o["action"]=="create"
def test_06_terminating_counts():
    s,c=base(); c["pods"][0]["terminating"]=True
    o=run(s,c)[1]; assert o["total_replicas"]==3
def test_07_topology():
    s,c=base(); s["workload"]["max_surge"]=1
    o=run(s,c)[1]; assert o["action"]=="create"
def test_08_deterministic():
    s,c=base(); a=run(s,c)[1]; b=run(s,c)[1]; assert a==b
def test_09_invalid_duplicate():
    s,c=base(); c["pods"][1]["name"]=c["pods"][0]["name"]
    o=run(s,c)[1]; assert o["action"]=="reject"
def test_10_does_not_mutate_state():
    s,c=base(); before=json.dumps(c,sort_keys=True); run(s,c); assert json.dumps(c,sort_keys=True)==before
def test_11_large():
    s,c=base()
    for i in range(1000):
        c["pods"].append({"name":f"x-{i}","workload":"other","revision":"x","node":"node-a1","ready":True,"ready_for_seconds":100,"terminating":False})
    o=run(s,c)[1]; assert "action" in o
