import subprocess,json
from pathlib import Path
R=Path("/app/repo")
def run(): return subprocess.run(["python","/app/scanner.py","--root","/app/repo","--config","/app/repo/.scanignore.json","--out","/tmp/report.sarif"],capture_output=True,text=True)
def rep(): return json.loads(Path("/tmp/report.sarif").read_text())
def results(): return rep()["runs"][0]["results"]
def test_01_runs(): assert run().returncode==0
def test_02_sarif_version(): assert rep()["version"]=="2.1.0"
def test_03_detect_generic_secret(): assert any(x["ruleId"]=="SECRET005" and "config.env" in x["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for x in results())
def test_04_detect_dep(): assert any(x["ruleId"]=="DEP002" for x in results())
def test_05_ignore_vendor(): assert not any("vendor/" in x["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for x in results())
def test_06_ignore_fixture(): assert not any("fixtures/" in x["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] for x in results())
def test_07_ignore_rule(): assert not any(x["ruleId"]=="DEP001" for x in results())
def test_08_no_absolute_paths(): assert all("/app/" not in json.dumps(x) for x in results())
def test_09_no_secret_value(): assert "not-a-placeholder-secret-value" not in Path("/tmp/report.sarif").read_text()
def test_10_deterministic(): a=Path("/tmp/report.sarif").read_bytes(); run(); assert Path("/tmp/report.sarif").read_bytes()==a
def test_11_sorted(): 
 r=results(); keys=[(x["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],x["locations"][0]["physicalLocation"]["region"]["startLine"],x["ruleId"]) for x in r]; assert keys==sorted(keys)
def test_12_fingerprint(): assert all("partialFingerprints" in x for x in results())
