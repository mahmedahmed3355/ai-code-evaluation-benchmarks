
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

APP=Path("/app"); DATA=APP/"data"; SOL=Path("/solution/reference_impl.py")

def run(events, reg=None, state=None):
    td=Path(tempfile.mkdtemp(prefix="cdc-test-"))
    (td/"events.jsonl").write_text("\n".join(json.dumps(x) for x in events)+"\n")
    if reg is None: reg=json.loads((DATA/"schema_registry.json").read_text())
    (td/"schema_registry.json").write_text(json.dumps(reg))
    shutil.copy(DATA/"schema_registry.json", td/"schema_registry.json")
    # Reference implementation reads /app/data/events.jsonl, so tests execute a temporary
    # self-contained clone by swapping files and restoring them.
    old=(DATA/"events.jsonl").read_text()
    (DATA/"events.jsonl").write_text((td/"events.jsonl").read_text())
    st=td/"state"; st.mkdir()
    if state:
        for n,v in state.items(): (st/n).write_text(v)
    env=os.environ.copy()
    env["PYTHONPATH"]="/solution"
    p=subprocess.run(["python",str(SOL)],cwd="/",env=env,capture_output=True,text=True)
    shutil.rmtree(td,ignore_errors=True)
    (DATA/"events.jsonl").write_text(old)
    return p

def read_state():
    s=Path("/app/state")
    return json.loads((s/"records.json").read_text()), json.loads((s/"checkpoint.json").read_text())

# Public tests are implemented as black-box contract checks against a fresh state.
# The student's cdc_sink.py is invoked by the local validation harness in the same way.

def write_fixture(events, state=None):
    DATA.joinpath("events.jsonl").write_text("\n".join(json.dumps(x) for x in events)+"\n")
    shutil.rmtree("/app/state",ignore_errors=True); Path("/app/state").mkdir()
    if state:
        for n,v in state.items(): Path("/app/state",n).write_text(v)

def invoke():
    return subprocess.run(["python","/app/cdc_sink.py","--events","/app/data/events.jsonl","--state-dir","/app/state"],capture_output=True,text=True)

def state():
    return json.loads(Path("/app/state/records.json").read_text()), json.loads(Path("/app/state/checkpoint.json").read_text())

def base():
    return [
      {"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A","balance":10}},
      {"partition":1,"offset":0,"key":"b","op":"upsert","schema_version":1,"payload":{"id":"b","name":"B","balance":20}},
    ]

def test_01_basic_multi_partition():
    write_fixture(base())
    p=invoke(); assert p.returncode==0
    r,c=state(); assert r["a"]["balance"]==10 and r["b"]["balance"]==20
    assert c["partitions"]=={"0":0,"1":0}

def test_02_partial_update():
    ev=base()+[{"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":2,"payload":{"email":"x@y"}}]
    write_fixture(ev); invoke()
    r,c=state(); assert r["a"]["name"]=="A" and r["a"]["email"]=="x@y"

def test_03_tombstone():
    ev=base()+[{"partition":0,"offset":1,"key":"a","op":"delete","schema_version":1,"payload":None}]
    write_fixture(ev); invoke()
    r,c=state(); assert "a" not in r and c["partitions"]["0"]==1

def test_04_replay_idempotent():
    ev=base()
    write_fixture(ev); invoke()
    first=state()
    invoke()
    assert state()==first

def test_05_interleaving():
    ev=[
      {"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A","balance":1}},
      {"partition":1,"offset":0,"key":"b","op":"upsert","schema_version":1,"payload":{"id":"b","name":"B","balance":2}},
      {"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":2,"payload":{"email":"a"}},
      {"partition":1,"offset":1,"key":"b","op":"upsert","schema_version":2,"payload":{"email":"b"}},
    ]
    write_fixture(ev); invoke()
    r,c=state(); assert c["partitions"]=={"0":1,"1":1} and r["a"]["email"]=="a"

def test_06_gap_rejected():
    ev=base()+[{"partition":0,"offset":2,"key":"a","op":"upsert","schema_version":1,"payload":{"balance":99}}]
    write_fixture(ev); invoke()
    r,c=state(); assert r["a"]["balance"]==10 and c["partitions"]["0"]==0

def test_07_additive_schema():
    ev=base()+[
      {"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":3,"payload":{"country":"EG"}}
    ]
    write_fixture(ev); invoke()
    r,c=state(); assert r["a"]["country"]=="EG" and c["partitions"]["0"]==1

def test_08_invalid_schema_transition():
    reg={"1":{"id":"string","name":"string"},"2":{"id":"string","name":"number"}}
    ev=[{"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A"}},
        {"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":2,"payload":{"name":5}}]
    write_fixture(ev); DATA.joinpath("schema_registry.json").write_text(json.dumps(reg))
    try:
        invoke(); r,c=state(); assert c["partitions"]["0"]==0
    finally:
        DATA.joinpath("schema_registry.json").write_text(json.dumps({
          "1":{"id":"string","name":"string","balance":"number"},
          "2":{"id":"string","name":"string","balance":"number","email":"string"},
          "3":{"id":"string","name":"string","balance":"number","email":"string","country":"string"}}))

def test_09_malformed_does_not_kill_other_partition():
    ev=[
      {"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A","balance":1}},
      {"partition":0,"offset":1,"key":"a","op":"wat","schema_version":1,"payload":{}},
      {"partition":1,"offset":0,"key":"b","op":"upsert","schema_version":1,"payload":{"id":"b","name":"B","balance":2}},
    ]
    write_fixture(ev); invoke()
    r,c=state(); assert "b" in r and c["partitions"]["0"]==0 and c["partitions"]["1"]==0

def test_10_corrupt_checkpoint_recovery():
    ev=base()+[{"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":2,"payload":{"email":"x"}}]
    write_fixture(ev, {"checkpoint.json":'{"partitions":{"0":999}}'})
    invoke()
    r,c=state(); assert c["partitions"]["0"]==1 and r["a"]["email"]=="x"

def test_11_large_stream():
    ev=[]
    for i in range(1500):
        ev.append({"partition":i%4,"offset":i//4,"key":f"k{i%17}","op":"upsert","schema_version":1,
                   "payload":{"id":f"k{i%17}","name":str(i),"balance":i}})
    write_fixture(ev); p=invoke()
    assert p.returncode==0
    r,c=state(); assert set(c["partitions"])=={"0","1","2","3"}
