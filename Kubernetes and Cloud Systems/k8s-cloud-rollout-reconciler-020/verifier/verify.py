
import json,subprocess
from pathlib import Path
def main():
 s=json.loads(Path("/app/data/spec.json").read_text()); c=json.loads(Path("/app/data/cluster_state.json").read_text())
 # Independent expected check for the supplied scenario: one create must be safe and
 # the selected node must preserve topology/resource feasibility.
 Path("/tmp/spec.json").write_text(json.dumps(s)); Path("/tmp/state.json").write_text(json.dumps(c))
 subprocess.run(["python","/app/reconcile.py","--spec","/tmp/spec.json","--state","/tmp/state.json","--out","/tmp/out.json"],check=True)
 o=json.loads(Path("/tmp/out.json").read_text())
 assert o["action"]=="create"
 assert o["pod"]=="payments-r2-0"
 assert o["node"] in {"node-a1","node-b1","node-b2","node-a2"}
 # Re-entrant determinism.
 subprocess.run(["python","/app/reconcile.py","--spec","/tmp/spec.json","--state","/tmp/state.json","--out","/tmp/out2.json"],check=True)
 assert json.loads(Path("/tmp/out2.json").read_text())==o
 print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
