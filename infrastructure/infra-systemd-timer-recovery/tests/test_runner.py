from pathlib import Path
import subprocess, sys, os

root=Path(os.environ.get("BENCH_ROOT", "/app"))
service=root/"environment/systemd/forge-maintenance.service"
timer=root/"environment/systemd/forge-maintenance.timer"
policy=root/"environment/systemd/maintenance-policy.conf"

def run(cmd):
    return subprocess.run(cmd,text=True,capture_output=True)

def ok(name, cond):
    print(f"{name}: {'PASS' if cond else 'FAIL'}")
    if not cond: raise AssertionError(name)

# Baseline must genuinely fail.
baseline=run(["python3",str(root/"environment/validate.sh")])
ok("baseline-fails", baseline.returncode != 0)

oracle=run(["/app/solution/solve.sh"])
ok("oracle-exits-zero", oracle.returncode == 0)
ok("oracle-pass", "VALIDATION=PASS" in oracle.stdout)

s=service.read_text()
t=timer.read_text()
p=policy.read_text()

checks={
 "oneshot": "Type=oneshot" in s,
 "non-root": "User=forge" in s and "Group=forge" in s,
 "command-preserved": "/usr/local/bin/forge-maintenance --run" in s,
 "timeout": "TimeoutStartSec=90s" in s,
 "memory": "MemoryMax=256M" in s,
 "cpu-weight": "CPUWeight=50" in s,
 "timer-persistent": "Persistent=true" in t,
 "timer-target": "Unit=forge-maintenance.service" in t,
 "lock-path": "LockPath=/var/lib/forge/maintenance.lock" in p,
 "lock-format": "LockFormat=generation,pid" in p,
 "live-owner": "LiveOwnerAction=refuse" in p,
 "stale-owner": "StaleOwnerAction=recover" in p,
 "failure": "FailurePublishesSuccess=no" in p,
 "overlap": "Overlap=refused" in p,
 "generation": "GenerationCheck=enabled" in p,
}
for k,v in checks.items(): ok(k,v)

blob=s+t+p
for bad in ["/bin/true","User=root","Persistent=no","RemainAfterExit=yes",
            "LiveOwnerAction=steal","FailurePublishesSuccess=yes"]:
    ok("reject-"+bad, bad not in blob)

hidden=run(["python3",str(root/"tests/hidden_tests.py")])
ok("hidden-tests", hidden.returncode==0 and "HIDDEN_TESTS=PASS" in hidden.stdout)

verify=run(["python3",str(root/"tests/verify.py")])
ok("independent-verifier", verify.returncode==0 and "VERIFIER=PASS" in verify.stdout)

print("TESTS=PASS")
