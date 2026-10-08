import csv,json,hashlib,os,shutil,subprocess,sys,tempfile
from pathlib import Path
import numpy as np
APP=Path("/app"); DATA=APP/"data"; PY=sys.executable
FEATURES=["age","income","balance","tenure","transactions","utilization"]
def cli(path):
    return subprocess.run([PY,"-m","ml_service",str(path)],cwd=APP,env={**os.environ,"PYTHONPATH":"/app"},text=True,capture_output=True)
def pred(path):
    p=cli(path); assert p.returncode==0,p.stderr; return np.asarray(json.loads(p.stdout)["predictions"],float)
def read(path):
    return list(csv.DictReader(open(path)))
def expected(rows,a):
    pp=a["preprocessing"]; x=np.array([[float(r[c]) if r[c]!="" else np.nan for c in FEATURES] for r in rows])
    x=np.where(np.isnan(x),pp["impute_mean"],x)
    for j,k in enumerate(pp["transform"]):
        if k=="log1p": x[:,j]=np.log1p(x[:,j])
        elif k=="signed_log1p": x[:,j]=np.sign(x[:,j])*np.log1p(np.abs(x[:,j]))
    x=np.clip(x,pp["clip_low"],pp["clip_high"]); x=(x-np.array(pp["scale_mean"]))/np.array(pp["scale_std"])
    w=np.array(a["weights"]); raw=np.c_[np.ones(len(x)),x]@w; z=raw/a["calibration"]["temperature"]+a["calibration"]["bias"]
    return 1/(1+np.exp(-np.clip(z,-60,60)))
def auc(y,s):
    order=np.argsort(s,kind="mergesort"); ss=s[order]; ranks=np.empty(len(s)); i=0
    while i<len(s):
        j=i+1
        while j<len(s) and ss[j]==ss[i]: j+=1
        ranks[order[i:j]]=(i+j+1)/2; i=j
    p=np.sum(y==1); n=np.sum(y==0); return (ranks[y==1].sum()-p*(p+1)/2)/(p*n)

def test_contract_exact():
    a=json.loads((DATA/"model_artifact.json").read_text()); rows=read(DATA/"nominal.csv"); assert np.allclose(pred(DATA/"nominal.csv"),expected(rows,a),atol=1e-12)
def test_reordered():
    assert np.allclose(pred(DATA/"nominal.csv"),pred(DATA/"reordered.csv"),atol=1e-12)
def test_missing():
    rows=read(DATA/"missing.csv"); p=pred(DATA/"missing.csv"); a=json.loads((DATA/"model_artifact.json").read_text()); assert np.allclose(p,expected(rows,a),atol=1e-12); assert np.all(np.isfinite(p))
def test_shifted_quality():
    rows=read(DATA/"shifted.csv"); y=np.array([int(r["target"]) for r in rows]); assert auc(y,pred(DATA/"shifted.csv"))>=0.72
def test_target_middle():
    rows=read(DATA/"nominal.csv")
    with tempfile.TemporaryDirectory() as td:
        q=Path(td)/"x.csv"
        with open(q,"w",newline="") as f:
            w=csv.writer(f); w.writerow(["income","target","age","balance","tenure","transactions","utilization"])
            for r in rows: w.writerow([r["income"],r["target"],r["age"],r["balance"],r["tenure"],r["transactions"],r["utilization"]])
        assert np.allclose(pred(q),pred(DATA/"nominal.csv"),atol=1e-12)
def test_duplicates_order():
    rows=read(DATA/"nominal.csv"); rows2=[rows[3],rows[3],rows[20],rows[3]]
    with tempfile.TemporaryDirectory() as td:
        q=Path(td)/"dup.csv"
        with open(q,"w",newline="") as f:
            w=csv.writer(f); w.writerow(FEATURES)
            for r in rows2: w.writerow([r[c] for c in FEATURES])
        p=pred(q); assert len(p)==4 and np.allclose(p[[0,1,3]],p[0],atol=1e-12)
def test_alternate_artifact():
    with tempfile.TemporaryDirectory() as td:
        q=Path(td)/"a.json"; shutil.copy2(DATA/"model_artifact.json",q)
        from ml_service.pipeline import predict
        assert np.allclose(predict(str(DATA/"nominal.csv"),str(q)),pred(DATA/"nominal.csv"),atol=1e-12)
def test_artifact_immutable():
    q=DATA/"model_artifact.json"; before=hashlib.sha256(q.read_bytes()).hexdigest()
    _=pred(DATA/"missing.csv"); _=pred(DATA/"nominal.csv")
    assert hashlib.sha256(q.read_bytes()).hexdigest()==before
def test_invalid_artifact_rejected():
    q=DATA/"model_artifact.json"; b=q.read_bytes()
    try:
        a=json.loads(b); a["feature_schema"]=list(reversed(a["feature_schema"])); q.write_text(json.dumps(a))
        p=cli(DATA/"nominal.csv"); assert p.returncode!=0 and "ERROR:" in p.stderr
    finally:q.write_bytes(b)
def test_invalid_schema_rejected():
    q=DATA/"schema.json"; b=q.read_bytes()
    try:
        a=json.loads(b); a["features"]=a["features"][:-1]; q.write_text(json.dumps(a))
        p=cli(DATA/"nominal.csv"); assert p.returncode!=0
    finally:q.write_bytes(b)
def test_evaluation_reentrant():
    from ml_service.preprocessing import load_artifact
    from ml_service.evaluation import evaluate
    a=load_artifact(); x=evaluate(str(DATA/"nominal.csv"),a); y=evaluate(str(DATA/"missing.csv"),a); z=evaluate(str(DATA/"nominal.csv"),a)
    assert np.isfinite(x) and np.isfinite(y) and abs(x-z)<1e-15
def main():
    tests=[v for k,v in globals().items() if k.startswith("test_")]
    for t in tests: t(); print(t.__name__,"PASS")
    print("TESTS=PASS")
if __name__=="__main__": main()
