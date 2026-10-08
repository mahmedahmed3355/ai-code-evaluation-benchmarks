import json
from pathlib import Path
def main():
    r=json.loads(Path("/tmp/report.sarif").read_text()); assert r["version"]=="2.1.0"
    xs=r["runs"][0]["results"]; assert any(x["ruleId"]=="SECRET005" for x in xs); assert any(x["ruleId"]=="DEP002" for x in xs)
    assert not any("vendor/" in json.dumps(x) or "fixtures/" in json.dumps(x) for x in xs)
    assert "not-a-placeholder-secret-value" not in Path("/tmp/report.sarif").read_text()
    print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
