import json,subprocess,hashlib
from pathlib import Path
def run(): return subprocess.run(["python","/app/promotion_gate.py","--candidate","/app/data/candidate.json","--registry","/app/data/registry.json","--out","/tmp/p.json"],capture_output=True,text=True)
def o(): return json.loads(Path("/tmp/p.json").read_text())
def test_01_accept(): run(); assert o()["decision"]=="promote"
def test_02_target(): assert o()["target_stage"]=="production"
def test_03_model(): assert o()["model_name"]=="fraud-detector"
def test_04_checksum_bad():
 c=json.loads(Path("/app/data/candidate.json").read_text()); c["artifact"]["sha256"]="0"*64; Path("/tmp/c.json").write_text(json.dumps(c)); subprocess.run(["python","/app/promotion_gate.py","--candidate","/tmp/c.json","--registry","/app/data/registry.json","--out","/tmp/x.json"]); assert json.loads(Path("/tmp/x.json").read_text())["decision"]=="reject"
def test_05_fake_delta():
 c=json.loads(Path("/app/data/candidate.json").read_text()); c["evaluation"]["metrics"]["auc"]=0.80; c["evaluation"]["delta"]={"auc":999}; Path("/tmp/c.json").write_text(json.dumps(c)); subprocess.run(["python","/app/promotion_gate.py","--candidate","/tmp/c.json","--registry","/app/data/registry.json","--out","/tmp/x.json"]); assert json.loads(Path("/tmp/x.json").read_text())["decision"]=="reject"
def test_06_deterministic(): run(); a=Path("/tmp/p.json").read_bytes(); run(); assert Path("/tmp/p.json").read_bytes()==a
def test_07_reasons_sorted(): assert o()["reasons"]==sorted(o()["reasons"])
def test_08_no_secret(): assert "MODEL-ARTIFACT" not in Path("/tmp/p.json").read_text()
def test_09_output_keys(): assert set(o())=={"decision","target_stage","model_name","version","reasons"}
def test_10_version_not_string_compare(): assert o()["version"]=="2.4.0"
def test_11_approval():
 c=json.loads(Path("/app/data/candidate.json").read_text()); c["approval"]["approved"]=False; Path("/tmp/c.json").write_text(json.dumps(c)); subprocess.run(["python","/app/promotion_gate.py","--candidate","/tmp/c.json","--registry","/app/data/registry.json","--out","/tmp/x.json"]); assert json.loads(Path("/tmp/x.json").read_text())["decision"]=="reject"
def test_12_missing_metric():
 c=json.loads(Path("/app/data/candidate.json").read_text()); del c["evaluation"]["metrics"]["auc"]; Path("/tmp/c.json").write_text(json.dumps(c)); subprocess.run(["python","/app/promotion_gate.py","--candidate","/tmp/c.json","--registry","/app/data/registry.json","--out","/tmp/x.json"]); assert json.loads(Path("/tmp/x.json").read_text())["decision"]=="reject"
