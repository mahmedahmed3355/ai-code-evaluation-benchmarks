from pathlib import Path
import os
import sys

root=Path(os.environ.get("BENCH_ROOT","/app"))/"environment"
s=(root/"systemd/forge-maintenance.service").read_text()
t=(root/"systemd/forge-maintenance.timer").read_text()
p=(root/"systemd/maintenance-policy.conf").read_text()

checks={
 "service_type": "Type=oneshot" in s,
 "identity": "User=forge" in s and "Group=forge" in s,
 "command": "/usr/local/bin/forge-maintenance --run" in s,
 "timeout": "TimeoutStartSec=90s" in s,
 "memory": "MemoryMax=256M" in s,
 "cpu": "CPUWeight=50" in s,
 "persistent": "Persistent=true" in t,
 "target": "Unit=forge-maintenance.service" in t,
 "lock_path": "LockPath=/var/lib/forge/maintenance.lock" in p,
 "lock_format": "LockFormat=generation,pid" in p,
 "live_owner": "LiveOwnerAction=refuse" in p,
 "stale_owner": "StaleOwnerAction=recover" in p,
 "failure": "FailurePublishesSuccess=no" in p,
 "overlap": "Overlap=refused" in p,
 "generation": "GenerationCheck=enabled" in p,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(f"{k}={'PASS' if v else 'FAIL'}")
if bad:
    print("VERIFIER=FAIL")
    sys.exit(1)
print("VERIFIER=PASS")
