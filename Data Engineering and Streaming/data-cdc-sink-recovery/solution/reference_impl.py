
import json, os, tempfile
from pathlib import Path

BASE=Path("/app")
DATA=BASE/"data"
STATE=BASE/"state"
STATE.mkdir(parents=True, exist_ok=True)
EVENTS=DATA/"events.jsonl"
REG=json.loads((DATA/"schema_registry.json").read_text())

def atomic(path, obj):
    path=Path(path); fd,tmp=tempfile.mkstemp(prefix=path.name+".", dir=str(path.parent))
    with os.fdopen(fd,"w") as f:
        json.dump(obj,f,sort_keys=True,separators=(",",":")); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)

def load_json(path, default):
    try: return json.loads(Path(path).read_text())
    except Exception: return default

def typok(v,t):
    if t=="string": return isinstance(v,str)
    if t=="number": return isinstance(v,(int,float)) and not isinstance(v,bool)
    if t=="integer": return isinstance(v,int) and not isinstance(v,bool)
    if t=="boolean": return isinstance(v,bool)
    return False

cp_path=STATE/"checkpoint.json"; rec_path=STATE/"records.json"
journal=STATE/"commit_journal.jsonl"; rej=STATE/"rejections.jsonl"

records=load_json(rec_path,{})
if not isinstance(records,dict): records={}
cp=load_json(cp_path,None)

def recover():
    by={}
    if journal.exists():
        for line in journal.read_text().splitlines():
            try:
                x=json.loads(line)
                p,o=x["partition"],x["offset"]
                if isinstance(p,int) and p>=0 and isinstance(o,int) and o>=0:
                    by.setdefault(p,set()).add(o)
            except Exception: pass
    out={}
    for p,vals in by.items():
        n=0
        while n in vals: n+=1
        if n: out[str(p)]=n-1
    return out

valid_cp=isinstance(cp,dict) and isinstance(cp.get("partitions",{}),dict)
if valid_cp:
    for p,o in cp["partitions"].items():
        if not (isinstance(p,str) and p.isdigit() and int(p)>=0 and isinstance(o,int) and not isinstance(o,bool) and o>=0):
            valid_cp=False; break
if not valid_cp:
    cp={"partitions":recover()}
    atomic(cp_path,cp)
parts=cp["partitions"]

# schema version per partition is persisted separately so restarts are deterministic.
sp_path=STATE/"schema_versions.json"
sp=load_json(sp_path,{})
if not isinstance(sp,dict): sp={}
# recover schema versions from accepted journal entries when absent is intentionally
# conservative: the journal may contain schema metadata in reference commits.
# We store it below.

seen_journal=set()
if journal.exists():
    for line in journal.read_text().splitlines():
        try:
            x=json.loads(line)
            seen_journal.add((x["partition"],x["offset"]))
        except Exception: pass

with EVENTS.open() as f:
  for raw in f:
    try:
      e=json.loads(raw)
    except Exception:
      continue
    if not isinstance(e,dict): continue
    p=e.get("partition"); o=e.get("offset"); k=e.get("key"); op=e.get("op"); sv=e.get("schema_version"); payload=e.get("payload")
    if not (isinstance(p,int) and not isinstance(p,bool) and p>=0 and isinstance(o,int) and not isinstance(o,bool) and o>=0 and isinstance(k,str) and k and isinstance(sv,int) and not isinstance(sv,bool) and sv>0): continue
    if str(p) in parts and o<=parts[str(p)]: continue
    expected=parts.get(str(p),-1)+1
    if o!=expected: continue
    if op not in ("upsert","delete") or str(sv) not in REG: continue
    schema=REG[str(sv)]
    if op=="delete":
      if payload is not None: continue
    else:
      if not isinstance(payload,dict): continue
      if "_key" in payload or "_schema_version" in payload: continue
      if any(field not in schema for field in payload): continue
      if any(not typok(v,schema[field]) for field,v in payload.items()): continue
    prev=int(sp[str(p)]) if str(p) in sp else None
    if prev is not None:
      if sv<prev: continue
      old=REG[str(prev)]
      if any(field not in schema or schema[field]!=t for field,t in old.items()): continue
    # idempotent crash recovery: if journal already contains this commit, repair cp only.
    if (p,o) in seen_journal:
      parts[str(p)]=o; sp[str(p)]=sv
      atomic(cp_path,{"partitions":parts}); atomic(sp_path,sp)
      continue
    # business effect
    if op=="delete":
      records.pop(k,None)
    else:
      r=records.get(k,{})
      if not isinstance(r,dict): r={}
      r=dict(r)
      r.update(payload)
      r["_key"]=k; r["_schema_version"]=sv
      records[k]=r
    atomic(rec_path,records)
    with journal.open("a") as jf:
      jf.write(json.dumps({"partition":p,"offset":o,"schema_version":sv},separators=(",",":"))+"\n")
      jf.flush(); os.fsync(jf.fileno())
    seen_journal.add((p,o)); parts[str(p)]=o; sp[str(p)]=sv
    atomic(cp_path,{"partitions":parts}); atomic(sp_path,sp)

atomic(rec_path,records)
