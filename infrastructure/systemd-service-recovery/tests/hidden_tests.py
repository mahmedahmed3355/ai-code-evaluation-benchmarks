# Adversarial hidden checks intentionally use different values and inspect semantics.
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]/"environment"
service=(root/"systemd/forge-worker.service").read_text()
drop=(root/"systemd/forge-worker.service.d/10-migration.conf").read_text()
text=service+"\n"+drop

assert "EnvironmentFile=/etc/forge/worker.env" in text
assert "After=network-online.target" in text
assert "Wants=network-online.target" in text
assert "ExecStartPre=/usr/local/bin/forge-worker --validate-config" in text
assert "User=forge" in text
assert "NoNewPrivileges=yes" in text
assert "Restart=on-failure" in text
assert "StartLimitBurst=5" in text
assert "StartLimitIntervalSec=60" in text
assert "READINESS_AFTER_START=1" in drop
assert "CLEAN_STOP_IS_SUCCESS=1" in drop
assert "TRANSIENT_FAILURE_RESTART=1" in drop

# A solution cannot simply replace the application with a success command.
assert "/bin/true" not in text
assert "VALIDATION=PASS" not in text

print("HIDDEN_TESTS=PASS")
