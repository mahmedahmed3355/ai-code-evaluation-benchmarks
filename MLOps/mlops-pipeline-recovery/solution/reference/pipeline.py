import argparse,json,hashlib,tempfile,os
from pathlib import Path
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--pipeline",required=True); ap.add_argument("--events",required=True); ap.add_argument("--state-dir",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
 p=json.load(open(a.pipeline)); stages={x["name"]:x for x in p["stages"]}; sd=Path(a.state_dir); sd.mkdir(exist_ok=True)
 j=sd/"journal.jsonl"; cp=sd/"checkpoint.json"; state={}
 try: state=json.loads(cp.read_text()).get("stages",{})
 except Exception: state={}
 if not isinstance(state,dict): state={}
 if j.exists():
  for line in j.read_text().splitlines():
   try:
    e=json.loads(line); n=e["stage"]; 
    if n in stages and isinstance(e.get("attempt"),int) and e["attempt"]>0: state[n]=e
   except Exception: pass
 seen={(n,x.get("status"),x.get("attempt")) for n,x in state.items()}
 for line in Path(a.events).read_text().splitlines():
  try: e=json.loads(line); n=e["stage"]; st=e["status"]; at=e["attempt"]
  except Exception: continue
  if n not in stages or st not in {"STARTED","SUCCEEDED","FAILED_RETRYABLE","FAILED_TERMINAL"} or not isinstance(at,int) or at<1: continue
  old=state.get(n)
  if old and at<old.get("attempt",0): continue
  if st=="SUCCEEDED":
   try: got=hashlib.sha256(Path(stages[n]["artifact"]["path"]).read_bytes()).hexdigest()
   except Exception: continue
   if got!=e.get("artifact_sha256") or got!=stages[n]["artifact"]["sha256"]: continue
   if any(state.get(d,{}).get("status")!="SUCCEEDED" for d in stages[n]["depends_on"]): continue
  state[n]=e
 def persist():
  tmp=cp.with_suffix(".tmp"); tmp.write_text(json.dumps({"stages":state},sort_keys=True)); os.replace(tmp,cp)
 persist()
 terminal=any(x.get("status")=="FAILED_TERMINAL" for x in state.values())
 if terminal: out={"action":"failed","stage":None,"attempt":0,"reason":"terminal_stage_failure","pipeline_status":"FAILED"}
 elif all(state.get(n,{}).get("status")=="SUCCEEDED" for n in stages):
  out={"action":"noop","stage":None,"attempt":0,"reason":"pipeline_complete","pipeline_status":"SUCCEEDED"}
 else:
  runnable=[]; blocked=False
  for n,s in stages.items():
   x=state.get(n,{})
   if x.get("status")=="SUCCEEDED": continue
   deps=s["depends_on"]
   if any(state.get(d,{}).get("status")=="FAILED_TERMINAL" for d in deps): blocked=True; continue
   if all(state.get(d,{}).get("status")=="SUCCEEDED" for d in deps):
    if x.get("status")=="FAILED_RETRYABLE" and x.get("attempt",0)<s["retry_limit"]: runnable.insert(0,n)
    elif x.get("status") not in {"STARTED","FAILED_RETRYABLE"}: runnable.append(n)
  if runnable:
   n=sorted(runnable)[0]; at=state.get(n,{}).get("attempt",0)+1
   out={"action":"run","stage":n,"attempt":at,"reason":"runnable_stage","pipeline_status":"RUNNING"}
  elif blocked: out={"action":"blocked","stage":None,"attempt":0,"reason":"dependency_failed","pipeline_status":"FAILED"}
  else: out={"action":"wait","stage":None,"attempt":0,"reason":"waiting_for_dependencies","pipeline_status":"RUNNING"}
 Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2))
if __name__=="__main__": main()
