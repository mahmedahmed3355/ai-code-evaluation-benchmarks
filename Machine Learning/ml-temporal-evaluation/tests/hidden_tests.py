import sys,pandas as pd,numpy as np
sys.path.insert(0,"/app"); from ml_eval.pipeline import evaluate
d=pd.read_csv("/app/data/events.csv"); b=evaluate(d)["auc"]; x=d.iloc[:40].copy(); x["event_id"]=[f"future-{i}" for i in range(40)]; x["timestamp"]="2025-01-25T00:00:00"; x["income"]=1e9; x["target"]=1-x["target"]; r=evaluate(pd.concat([d,x],ignore_index=True)); assert abs(r["auc"]-b)<1e-12 and r["future_rows_ignored"]==130
z=d.sample(frac=1,random_state=3).reset_index(drop=True); z.loc[:8,"events_30d"]=np.nan; assert 0<=evaluate(z)["auc"]<=1
print("PASS hidden tests")
