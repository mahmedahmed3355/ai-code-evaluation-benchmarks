import csv,json,os,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
APP=Path("/app"); DATA=APP/"data"
# Hidden adversarial checks: feature order, missingness, large chunked input, and calibration.
def run(p):
    return subprocess.run([sys.executable,"-m","ml_service",str(p)],cwd=APP,env={**os.environ,"PYTHONPATH":"/app"},text=True,capture_output=True)
with tempfile.TemporaryDirectory() as td:
    q=Path(td)/"large.csv"; rng=np.random.default_rng(991)
    with open(q,"w",newline="") as f:
        w=csv.writer(f); w.writerow(["utilization","age","transactions","balance","income","tenure"])
        for i in range(2048):
            w.writerow([.3+i%10/100,30+i%20,10+i%15,10000+i,50000+i*3,4+i%5])
    p=run(q); assert p.returncode==0,p.stderr
    vals=np.asarray(json.loads(p.stdout)["predictions"]); assert len(vals)==2048 and np.all(np.isfinite(vals))
a=json.loads((DATA/"model_artifact.json").read_text())
assert a["calibration"]["temperature"]==1.25 and a["calibration"]["bias"]==-0.10
print("HIDDEN_TESTS=PASS")
