import json,re
from pathlib import Path
def main():
    t=Path("/app/service/Dockerfile").read_text(); p=json.loads(Path("/app/service/runtime-policy.json").read_text())
    assert re.search(r"(?im)^USER\\s+10001(?::10001)?\\s*$",t)
    assert "chmod -R 777" not in t and "latest" not in t.lower()
    assert ".env.production" not in t and "secrets" not in t.lower()
    assert p["read_only_rootfs"] and p["no_new_privileges"] and p["capabilities_drop"]==["ALL"] and not p["privileged"]
    assert "/tmp" in p["tmpfs"]
    print("INDEPENDENT_VERIFIER_PASS")
if __name__=="__main__": main()
