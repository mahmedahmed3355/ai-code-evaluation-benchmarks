
import json,subprocess
from pathlib import Path
def run(s,c):
 Path("/tmp/s.json").write_text(json.dumps(s)); Path("/tmp/c.json").write_text(json.dumps(c))
 subprocess.run(["python","/app/reconcile.py","--spec","/tmp/s.json","--state","/tmp/c.json","--out","/tmp/o.json"],check=True)
 return json.loads(Path("/tmp/o.json").read_text())
def mk():
 s=json.loads(Path("/app/data/spec.json").read_text()); c=json.loads(Path("/app/data/cluster_state.json").read_text()); return s,c
def test_h01_adversarial_node_order():
 s,c=mk(); c["nodes"]=list(reversed(c["nodes"])); a=run(s,c); c["nodes"]=list(reversed(c["nodes"])); b=run(s,c); assert a==b
def test_h02_memory_fragmentation():
 s,c=mk()
 for n in c["nodes"]: n["used"]["memory_mib"]=3600
 c["nodes"][3]["used"]["memory_mib"]=3000
 o=run(s,c); assert o["action"]=="create" and o["node"]==c["nodes"][3]["name"]
def test_h03_unready_node_excluded():
 s,c=mk(); c["nodes"][0]["ready"]=False
 o=run(s,c); assert o["node"]!="node-a1" if o["action"]=="create" else True
def test_h04_topology_domain_zero():
 s,c=mk(); c["nodes"].append({"name":"node-c1","zone":"c","ready":True,"allocatable":{"cpu_m":4000,"memory_mib":4096},"used":{"cpu_m":0,"memory_mib":0}})
 o=run(s,c); assert o["action"]=="create" and o["node"]=="node-c1"
def test_h05_old_unavailable_cannot_delete():
 s,c=mk(); s["workload"]["max_surge"]=0
 c["pods"][0]["ready"]=False
 o=run(s,c); assert o["action"]=="wait"
def test_h06_pdb_strict():
 s,c=mk(); s["workload"]["max_surge"]=0; s["workload"]["replicas"]=3; s["pdb"]["min_available"]=3
 o=run(s,c); assert o["action"]=="wait"
def test_h07_reserved_extra_pod():
 s,c=mk(); c["pods"].append({"name":"payments-r2-0","workload":"payments","revision":"r2","node":"node-b2","ready":True,"ready_for_seconds":50,"terminating":False})
 o=run(s,c); assert o["pod"]!="payments-r2-0"
def test_h08_non_workload_pods_ignored():
 s,c=mk(); c["pods"] += [{"name":f"other-{i}","workload":"x","revision":"z","node":"node-a1","ready":True,"ready_for_seconds":100,"terminating":False} for i in range(100)]
 o=run(s,c); assert o["action"]=="create"
def test_h09_invalid_negative_request():
 s,c=mk(); s["pod_template"]["requests"]["cpu_m"]=-1
 o=run(s,c); assert o["action"]=="reject"
def test_h10_missing_node_reference():
 s,c=mk(); c["pods"][0]["node"]="ghost"
 o=run(s,c); assert o["action"]=="reject"
