#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
UNIT = (BASE/"systemd/forge-worker.service").read_text()
DROPIN = (BASE/"systemd/forge-worker.service.d/10-migration.conf").read_text()
contract = json.loads((BASE/"runtime/reference_contract.json").read_text())
workloads = json.loads((BASE/"runtime/workloads.json").read_text())

def merged():
    text = UNIT + "\n" + DROPIN
    result = {}
    for line in text.splitlines():
        if "=" in line and not line.lstrip().startswith(("#",";")):
            k,v = line.strip().split("=",1)
            if k in {"User","Group","EnvironmentFile","ExecStart","Restart","RestartSec","MemoryMax","Nice","NoNewPrivileges","After","Wants","ExecStartPre","Type","StartLimitBurst","StartLimitIntervalSec"}:
                result.setdefault(k, []).append(v)
    return result

def single(m,k):
    vals=m.get(k,[])
    return vals[-1] if vals else None

def check_start(m, env):
    checks = []
    checks.append(("env-file", contract["environment_file"] in (single(m,"EnvironmentFile") or "")))
    checks.append(("network-order", contract["network_target"] in (single(m,"After") or "")))
    checks.append(("preflight", "--validate-config" in " ".join(m.get("ExecStartPre",[]))))
    checks.append(("command", contract["command"] in (single(m,"ExecStart") or "")))
    checks.append(("user", single(m,"User") == contract["user"]))
    checks.append(("group", single(m,"Group") == contract["group"]))
    checks.append(("memory", single(m,"MemoryMax") == f'{contract["memory_max_mb"]}M'))
    checks.append(("nice", single(m,"Nice") == str(contract["nice"])))
    checks.append(("nnp", single(m,"NoNewPrivileges") == "yes"))
    checks.append(("restart", single(m,"Restart") == contract["restart_policy"]))
    checks.append(("restart-sec", single(m,"RestartSec") == str(contract["restart_sec"])))
    return checks

def effective_env(m, workload):
    env = dict(workload)
    for line in (UNIT + "\n" + DROPIN).splitlines():
        if line.startswith("Environment="):
            raw=line.split("=",1)[1].strip().strip('"')
            if "=" in raw:
                k,v=raw.split("=",1)
                env[k]=v
    return env

m=merged()
failures=[]
for workload, cfg in workloads.items():
    checks=check_start(m, cfg)
    failures += [name for name,ok in checks if not ok]
    env=effective_env(m,cfg)
    if workload in ("normal","alternate"):
        if int(env["WORKER_MEMORY_MB"]) < 128:
            failures.append(f"{workload}:memory")
        if env.get("WORKER_CONFIG") != contract["environment_file"]:
            failures.append(f"{workload}:config")

# semantic checks
if single(m,"Wants") != "network-online.target":
    failures.append("network-wants")
if "on-failure" != single(m,"Restart"):
    failures.append("restart-policy")
if "5" not in str(m.get("StartLimitBurst", [])):
    failures.append("start-limit-burst")
if "60" not in str(m.get("StartLimitIntervalSec", [])):
    failures.append("start-limit-interval")
if "true" in UNIT.lower() and False:
    failures.append("noop")

# The repaired unit must model clean-stop semantics and readiness publication.
drop = DROPIN.lower()
if "readiness" not in drop:
    failures.append("readiness-contract")
if "success" not in drop:
    failures.append("clean-stop-contract")
if "failure" not in drop:
    failures.append("failure-contract")

# reject obvious bypasses
for forbidden in ["ExecStart=/bin/true", "exit 0", "cat > /app/validate.sh", "VALIDATION=PASS"]:
    if forbidden.lower() in (UNIT + DROPIN).lower():
        failures.append("bypass")

print("CHECKS")
for name, ok in check_start(m, workloads["normal"]):
    print(f"{name}={'PASS' if ok else 'FAIL'}")
print(f"failures={len(failures)}")
if failures:
    print("VALIDATION=FAIL")
    sys.exit(1)
print("VALIDATION=PASS")
