import json
from pathlib import Path
def main():
    o=json.loads(Path("/tmp/decision.json").read_text())
    assert set(o)=={"action","stage","attempt","reason","pipeline_status"}
    assert o["action"] in {"run","wait","blocked","failed","noop"}
    print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
