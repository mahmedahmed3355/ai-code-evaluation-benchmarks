
import json, os, shutil, subprocess, tempfile
from pathlib import Path

def prep(events, cp=None, journal=None):
    shutil.rmtree("/app/state",ignore_errors=True); Path("/app/state").mkdir()
    Path("/app/data/events.jsonl").write_text("\n".join(
        x if isinstance(x,str) else json.dumps(x) for x in events)+"\n")
    if cp is not None: Path("/app/state/checkpoint.json").write_text(cp)
    if journal is not None: Path("/app/state/commit_journal.jsonl").write_text(journal)

def run(): return subprocess.run(["python","/app/cdc_sink.py","--events","/app/data/events.jsonl","--state-dir","/app/state"],capture_output=True,text=True)
def st():
    return json.loads(Path("/app/state/records.json").read_text()),json.loads(Path("/app/state/checkpoint.json").read_text())

def test_hidden_01_duplicate_same_offset_different_delivery():
    e={"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,"payload":{"id":"x","name":"X","balance":1}}
    prep([e,e]); assert run().returncode==0; r,c=st(); assert r["x"]["balance"]==1 and c["partitions"]["0"]==0

def test_hidden_02_delete_absent_is_commit():
    prep([{"partition":2,"offset":0,"key":"ghost","op":"delete","schema_version":1,"payload":None}])
    run(); r,c=st(); assert "ghost" not in r and c["partitions"]["2"]==0

def test_hidden_03_partition_schema_independence():
    prep([
      {"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A","balance":1}},
      {"partition":1,"offset":0,"key":"b","op":"upsert","schema_version":2,"payload":{"id":"b","name":"B","balance":2,"email":"b"}},
      {"partition":0,"offset":1,"key":"a","op":"upsert","schema_version":1,"payload":{"balance":3}},
    ])
    run(); r,c=st(); assert c["partitions"]=={"0":1,"1":0}

def test_hidden_04_reserved_field_injection():
    prep([{"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,
           "payload":{"id":"x","name":"X","balance":1,"_key":"evil"}}])
    run(); r,c=st(); assert c["partitions"]=={} and r=={}

def test_hidden_05_future_offset_after_rejection_stays_gap():
    prep([
      {"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,"payload":{"id":"x","name":"X","balance":1}},
      {"partition":0,"offset":1,"key":"x","op":"upsert","schema_version":1,"payload":{"unknown":1}},
      {"partition":0,"offset":2,"key":"x","op":"upsert","schema_version":1,"payload":{"balance":2}},
    ])
    run(); r,c=st(); assert r["x"]["balance"]==1 and c["partitions"]["0"]==0

def test_hidden_06_sparse_journal_never_skips():
    prep([{"partition":0,"offset":2,"key":"x","op":"upsert","schema_version":1,"payload":{"id":"x","name":"X","balance":2}}],
         cp='{"broken":true}', journal='{"partition":0,"offset":2}\n')
    run(); r,c=st(); assert c["partitions"]=={} and r=={}

def test_hidden_07_malformed_json_between_valid_events():
    prep([
      '{"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,"payload":{"id":"x","name":"X","balance":1}}',
      '{"not-json"',
      '{"partition":1,"offset":0,"key":"y","op":"upsert","schema_version":1,"payload":{"id":"y","name":"Y","balance":2}}'
    ])
    run(); r,c=st(); assert "x" in r and "y" in r

def test_hidden_08_type_validation():
    prep([{"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,
           "payload":{"id":"x","name":"X","balance":"not-a-number"}}])
    run(); r,c=st(); assert r=={} and c["partitions"]=={}

def test_hidden_09_reentrant_convergence_after_tombstone():
    prep([
      {"partition":0,"offset":0,"key":"x","op":"upsert","schema_version":1,"payload":{"id":"x","name":"X","balance":1}},
      {"partition":0,"offset":1,"key":"x","op":"delete","schema_version":1,"payload":None}
    ])
    run(); first=st(); run(); assert st()==first

def test_hidden_10_partition_zero_and_large_partition():
    prep([
      {"partition":0,"offset":0,"key":"a","op":"upsert","schema_version":1,"payload":{"id":"a","name":"A","balance":1}},
      {"partition":999,"offset":0,"key":"z","op":"upsert","schema_version":1,"payload":{"id":"z","name":"Z","balance":9}},
    ])
    run(); r,c=st(); assert c["partitions"]=={"0":0,"999":0}
