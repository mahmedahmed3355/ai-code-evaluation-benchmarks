#!/bin/bash
set -euo pipefail

systemctl daemon-reload
systemctl enable backend.service
systemctl restart backend.service

python3 - <<'PY'
from pathlib import Path
p = Path('/etc/nginx/sites-available/backend')
s = p.read_text()
s = s.replace('unix:/run/backend/wrong.sock', 'unix:/run/backend/orders.sock')
p.write_text(s)
PY

nginx -t
systemctl enable --now nginx.service
systemctl restart nginx.service

for _ in $(seq 1 20); do
  if curl -fsS http://127.0.0.1/health >/dev/null && curl -fsS http://127.0.0.1/api/v1/orders/A-100 >/dev/null; then
    exit 0
  fi
  sleep 1
done
exit 1
