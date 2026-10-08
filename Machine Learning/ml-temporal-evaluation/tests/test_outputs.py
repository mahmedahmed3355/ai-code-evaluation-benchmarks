import sys,json
sys.path.insert(0,"/app"); import pandas as pd,numpy as np
from ml_eval.pipeline import evaluate
D="/app/data/events.csv"; A="/app/data/model_artifact.json"
def test_nominal():
 d=pd.read_csv(D); r=evaluate(d); assert r["train_rows"]==180 and r["validation_rows"]==180 and r["future_rows_ignored"]==90
def test_reorder_missing():
 d=pd.read_csv(D); b=evaluate(d)["auc"]; d=d[["target","events_30d","event_id","income","timestamp","balance"]]; d.loc[180:190,"income"]=np.nan; assert 0<=evaluate(d)["auc"]<=1

def test_future():
 d=pd.read_csv(D); b=evaluate(d)["auc"]; d.loc[d.timestamp>"2025-01-20T23:59:59","income"]=1e9; assert abs(evaluate(d)["auc"]-b)<1e-12
def test_dupe():
 d=pd.read_csv(D); d.loc[1,"event_id"]=d.loc[0,"event_id"]
 try:evaluate(d); assert False
 except ValueError as e: assert "duplicate" in str(e)
def test_immutability():
 d=pd.read_csv(D); before=d.copy(deep=True); raw=open(A,"rb").read(); a=evaluate(d); b=evaluate(d); assert a==b and open(A,"rb").read()==raw; pd.testing.assert_frame_equal(d,before)
def test_alt_artifact():
 d=pd.read_csv(D); a=json.load(open(A)); a["bias"]+=.2; p="/tmp/a.json"; json.dump(a,open(p,"w")); assert abs(evaluate(d,artifact_path=A)["auc"]-evaluate(d,artifact_path=p)["auc"])>1e-8
for n,v in list(globals().items()):
 if n.startswith("test_"): v(); print("PASS",n)
