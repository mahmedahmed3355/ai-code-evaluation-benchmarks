#!/bin/sh
set -eu

cat > ${BENCH_ROOT:-/app}/environment/systemd/forge-maintenance.service <<'EOF'
[Unit]
Description=Forge maintenance job
After=basic.target

[Service]
Type=oneshot
User=forge
Group=forge
ExecStart=/usr/local/bin/forge-maintenance --run
TimeoutStartSec=90s
MemoryMax=256M
CPUWeight=50
RemainAfterExit=no
EOF

cat > ${BENCH_ROOT:-/app}/environment/systemd/forge-maintenance.timer <<'EOF'
[Unit]
Description=Forge maintenance schedule

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h
Persistent=true
Unit=forge-maintenance.service

[Install]
WantedBy=timers.target
EOF

cat > ${BENCH_ROOT:-/app}/environment/systemd/maintenance-policy.conf <<'EOF'
[Maintenance]
LockPath=/var/lib/forge/maintenance.lock
StateDir=/var/lib/forge/maintenance
LockFormat=generation,pid
LiveOwnerAction=refuse
StaleOwnerAction=recover
FailurePublishesSuccess=no
Overlap=refused
GenerationCheck=enabled
EOF

cd "${BENCH_ROOT:-/app}"
./environment/validate.sh
