#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../environment" && pwd)
mkdir -p "$ROOT/systemd/forge-worker.service.d"
cat > "$ROOT/systemd/forge-worker.service" <<'EOF'
[Unit]
Description=Forge Worker
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=forge
Group=forge
EnvironmentFile=/etc/forge/worker.env
ExecStartPre=/usr/local/bin/forge-worker --validate-config
ExecStart=/usr/local/bin/forge-worker --serve
Restart=on-failure
RestartSec=3
StartLimitBurst=5
StartLimitIntervalSec=60
MemoryMax=512M
Nice=5
NoNewPrivileges=yes
EOF
cat > "$ROOT/systemd/forge-worker.service.d/10-migration.conf" <<'EOF'
[Service]
Environment="WORKER_CONFIG=/etc/forge/worker.env"
Environment="WORKER_USER=forge"
Environment="WORKER_MEMORY_MB=512"
Environment="READINESS_AFTER_START=1"
Environment="CLEAN_STOP_IS_SUCCESS=1"
Environment="TRANSIENT_FAILURE_RESTART=1"
EOF
"$ROOT/validate.sh"
