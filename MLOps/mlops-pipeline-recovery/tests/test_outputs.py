import json,subprocess,shutil
from pathlib import Path
def run(events=None,state=None):
 if events is None: events=[{"stage":"prepare","status":"STARTED","attempt":1},{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":""}]
 p=Path("/tmp/events.jsonl"); p.write_text("\\n".join(json.dumps(x) for x in events)+"\\n")
 sd=Path("/tmp/state"); shutil.rmtree(sd,ignore_errors=True); sd.mkdir()
 if state:
  for k,v in state.items(): (sd/k).write_text(v)
 return subprocess.run(["python","/app/pipeline.py","--pipeline","/app/data/pipeline.json","--events",str(p),"--state-dir",str(sd), "--out","/tmp/decision.json"],capture_output=True,text=True)
def out(): return json.loads(Path("/tmp/decision.json").read_text())
def test_01_next_stage():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}]); assert out()["stage"]=="train"
def test_02_deterministic():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}]); a=Path("/tmp/decision.json").read_bytes(); run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}]); assert Path("/tmp/decision.json").read_bytes()==a
def test_03_bad_checksum():
 run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":"0"*64}]); assert out()["stage"]=="prepare"
def test_04_malformed_event():
 run([{"stage":"ghost","status":"SUCCEEDED","attempt":1}]); assert out()["stage"]=="prepare"
def test_05_output_keys():
 run(); assert set(out())=={"action","stage","attempt","reason","pipeline_status"}
def test_06_attempt_positive():
 run([{"stage":"prepare","status":"STARTED","attempt":0}]); assert out()["stage"]=="prepare"
def test_07_dependency():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 run([{"stage":"train","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}]); assert out()["stage"]=="prepare"
def test_08_retry_priority():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h},{"stage":"train","status":"FAILED_RETRYABLE","attempt":1}]); assert out()["stage"]=="train"
def test_09_terminal_failure():
 run([{"stage":"prepare","status":"FAILED_TERMINAL","attempt":1}]); assert out()["action"]=="failed"
def test_10_corrupt_checkpoint():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}],{"checkpoint.json":"{bad","journal.jsonl":json.dumps({"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h})+"\n"}); assert out()["stage"]=="train"
def test_11_missing_artifact():
 import hashlib
 h=hashlib.sha256(Path("/app/data/prepare.bin").read_bytes()).hexdigest()
 Path("/app/data/train.bin").unlink()
 try:
  run([{"stage":"prepare","status":"SUCCEEDED","attempt":1,"artifact_sha256":h}]); assert out()["stage"]=="train"
 finally:
  Path("/app/data/train.bin").write_text("train-output-v1")
def test_12_no_secret_content(): run(); assert "prepare-output" not in Path("/tmp/decision.json").read_text()
