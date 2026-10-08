from pathlib import Path
import json, os

root=Path(os.environ.get("BENCH_ROOT","/app"))/"environment"
s=(root/"systemd/forge-maintenance.service").read_text()
t=(root/"systemd/forge-maintenance.timer").read_text()
p=(root/"systemd/maintenance-policy.conf").read_text()
sc=json.loads((root/"runtime/scenarios.json").read_text())

assert len(sc)==5
assert "LockFormat=generation,pid" in p
assert "GenerationCheck=enabled" in p
assert "LiveOwnerAction=refuse" in p
assert "StaleOwnerAction=recover" in p
assert "Overlap=refused" in p
assert "FailurePublishesSuccess=no" in p
assert "Persistent=true" in t
assert "Type=oneshot" in s
assert "User=forge" in s
assert "Group=forge" in s
assert "TimeoutStartSec=90s" in s
assert "MemoryMax=256M" in s
assert "CPUWeight=50" in s
assert "/usr/local/bin/forge-maintenance --run" in s

# No trivial bypass or destructive recovery.
blob=s+t+p
for bad in ["/bin/true","User=root","Persistent=no",
            "LockMode=unconditional-delete","LiveOwnerAction=steal",
            "FailurePublishesSuccess=yes"]:
    assert bad not in blob

print("HIDDEN_TESTS=PASS")
