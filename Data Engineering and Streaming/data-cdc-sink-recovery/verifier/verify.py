
"""
Independent verifier for data-cdc-sink-recovery-019.

It intentionally does not import the candidate implementation. It generates an
event stream and computes expected behavior using a compact independent model.
"""
import json, os, subprocess, tempfile, shutil, random
from pathlib import Path

ROOT=Path("/app")
EVENTS=ROOT/"data/events.jsonl"
STATE=ROOT/"state"

REG={
 "1":{"id":"string","name":"string","balance":"number"},
 "2":{"id":"string","name":"string","balance":"number","email":"string"},
 "3":{"id":"string","name":"string","balance":"number","email":"string","country":"string"},
}

def ok(v,t):
    return (t=="string" and isinstance(v,str)) or (t=="number" and isinstance(v,(int,float)) and not isinstance(v,bool))

def model(events):
    rec={}; cp={}; sv={}
    for e in events:
        if not isinstance(e,dict): continue
        p,o,k,op,v,pay=(e.get(x) for x in ("partition","offset","key","op","schema_version","payload"))
        if not (isinstance(p,int) and p>=0 and isinstance(o,int) and o>=0 and isinstance(k,str) and k and isinstance(v,int) and v>0): continue
        if o<=cp.get(p,-1): continue
        if o!=cp.get(p,-1)+1 or str(v) not in REG or op not in ("upsert","delete"): continue
        if op=="delete":
            if pay is not None: continue
        else:
            if not isinstance(pay,dict) or "_key" in pay or "_schema_version" in pay: continue
            if any(f not in REG[str(v)] or not ok(x,REG[str(v)][f]) for f,x in pay.items()): continue
        if p in sv:
            old=REG[str(sv[p])]
            if v<sv[p] or any(f not in REG[str(v)] or REG[str(v)][f]!=t for f,t in old.items()): continue
        if op=="delete": rec.pop(k,None)
        else:
            r=dict(rec.get(k,{})); r.update(pay); r["_key"]=k; r["_schema_version"]=v; rec[k]=r
        cp[p]=o; sv[p]=v
    return rec, {"partitions":{str(k):v for k,v in sorted(cp.items())}}

def main():
    rng=random.Random(19019)
    events=[]
    offsets=[0,0,0]
    for i in range(240):
        p=rng.randrange(3); o=offsets[p]; offsets[p]+=1
        key=f"k{rng.randrange(11)}"
        if i%17==0:
            e={"partition":p,"offset":o,"key":key,"op":"delete","schema_version":1,"payload":None}
        else:
            v=1 if o<4 else (2 if o<8 else 3)
            fields={"balance":rng.randrange(1000)}
            if o==0: fields.update({"id":key,"name":key})
            if v>=2 and o%3==0: fields["email"]=f"{key}@x"
            if v>=3 and o%5==0: fields["country"]="EG"
            e={"partition":p,"offset":o,"key":key,"op":"upsert","schema_version":v,"payload":fields}
        events.append(e)
        if i%29==0: events.append(dict(e))  # replay
    EVENTS.write_text("\n".join(json.dumps(x) for x in events)+"\n")
    shutil.rmtree(STATE,ignore_errors=True); STATE.mkdir()
    subprocess.run(["python","/app/cdc_sink.py","--events",str(EVENTS),"--state-dir",str(STATE)],check=True)
    actual=json.loads((STATE/"records.json").read_text()),json.loads((STATE/"checkpoint.json").read_text())
    expected=model(events)
    if actual!=expected: raise SystemExit(f"independent verifier mismatch: {actual!r} != {expected!r}")
    subprocess.run(["python","/app/cdc_sink.py","--events",str(EVENTS),"--state-dir",str(STATE)],check=True)
    actual2=json.loads((STATE/"records.json").read_text()),json.loads((STATE/"checkpoint.json").read_text())
    if actual2!=expected: raise SystemExit("re-entrant execution changed committed state")
    print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
