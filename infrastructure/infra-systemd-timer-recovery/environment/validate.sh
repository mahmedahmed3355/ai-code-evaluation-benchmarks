#!/usr/bin/env python3
import json, sys, os
from pathlib import Path

base=Path(os.environ.get("BENCH_ROOT", "/app"))
service=(base/"environment/systemd/forge-maintenance.service").read_text()
timer=(base/"environment/systemd/forge-maintenance.timer").read_text()
policy=(base/"environment/systemd/maintenance-policy.conf").read_text()
contract=json.loads((base/"environment/runtime/contract.json").read_text())
scenarios=json.loads((base/"environment/runtime/scenarios.json").read_text())

fail=[]

def need(name, cond):
    if not cond: fail.append(name)

need("service-command", contract["command"] in service)
need("non-root", "User=forge" in service and "Group=forge" in service)
need("timeout", "TimeoutStartSec=90s" in service)
need("memory", "MemoryMax=256M" in service)
need("cpu-weight", "CPUWeight=50" in service)
need("oneshot", "Type=oneshot" in service)
need("no-remain-after-exit", "RemainAfterExit=no" in service)

need("timer-persistent", "Persistent=true" in timer)
need("timer-service", "Unit=forge-maintenance.service" in timer)
need("no-overlap", "Persistent=true" in timer and "Type=oneshot" in service)

# Policy is intentionally represented as a declarative launcher contract.
need("lock-file", "LockPath=/var/lib/forge/maintenance.lock" in policy)
need("state-dir", "StateDir=/var/lib/forge/maintenance" in policy)
need("lock-format", "LockFormat=generation,pid" in policy)
need("live-owner-protection", "LiveOwnerAction=refuse" in policy)
need("stale-recovery", "StaleOwnerAction=recover" in policy)
need("failure-propagation", "FailurePublishesSuccess=no" in policy)
need("generation-check", "GenerationCheck=enabled" in policy)

# Scenario semantics: the policy must imply safe outcomes.
if "LiveOwnerAction=refuse" not in policy:
    fail.append("live-owner-safety")
if "StaleOwnerAction=recover" not in policy:
    fail.append("stale-recovery")
if "Overlap=refused" not in policy:
    fail.append("overlap")
if "GenerationCheck=enabled" not in policy:
    fail.append("generation")

# Explicit bypass protection.
bad=["/bin/true", "User=root", "FailurePublishesSuccess=yes",
     "LiveOwnerAction=steal", "LockMode=unconditional-delete",
     "Persistent=no", "RemainAfterExit=yes"]
blob=service+"\n"+timer+"\n"+policy
for item in bad:
    if item in blob:
        fail.append("forbidden:"+item)

print("SYSTEMD_RECOVERY_VALIDATION")
print("scenarios="+str(len(scenarios)))
print("failures="+str(len(fail)))
if fail:
    for x in fail: print("FAIL:"+x)
    print("VALIDATION=FAIL")
    sys.exit(1)
print("VALIDATION=PASS")
