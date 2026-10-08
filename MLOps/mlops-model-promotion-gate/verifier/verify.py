import json
from pathlib import Path
def main():
    o=json.loads(Path("/tmp/p.json").read_text()); assert o["decision"]=="promote"; assert o["target_stage"]=="production"
    assert o["reasons"]==[]
    print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
