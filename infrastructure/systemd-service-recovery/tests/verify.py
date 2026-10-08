import subprocess, sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]/"environment"
service=(root/"systemd/forge-worker.service").read_text()
drop=(root/"systemd/forge-worker.service.d/10-migration.conf").read_text()
text=service+"\n"+drop

checks = {
 "real_command": "/usr/local/bin/forge-worker --serve" in service,
 "preflight": "--validate-config" in service,
 "network_order": "After=network-online.target" in service and "Wants=network-online.target" in service,
 "config_source": "EnvironmentFile=/etc/forge/worker.env" in service,
 "least_privilege": "User=forge" in service and "Group=forge" in service,
 "resource_contract": "MemoryMax=512M" in service and "Nice=5" in service,
 "security_contract": "NoNewPrivileges=yes" in service,
 "failure_restart": "Restart=on-failure" in service and "RestartSec=3" in service,
 "rate_limit": "StartLimitBurst=5" in service and "StartLimitIntervalSec=60" in service,
 "readiness": "READINESS_AFTER_START=1" in drop,
 "clean_stop": "CLEAN_STOP_IS_SUCCESS=1" in drop,
 "transient_recovery": "TRANSIENT_FAILURE_RESTART=1" in drop,
 "no_shell": "/bin/sh" not in service,
 "no_bypass": all(x not in text.lower() for x in ["/bin/true","validation=pass","execstart=/bin/false"])
}
bad=[k for k,v in checks.items() if not v]
print("INDEPENDENT_VERIFIER")
for k,v in checks.items(): print(f"{k}={'PASS' if v else 'FAIL'}")
if bad:
    print("VERIFIER=FAIL")
    sys.exit(1)
print("VERIFIER=PASS")
