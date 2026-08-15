#!/bin/bash
set -euo pipefail

systemctl daemon-reload

systemctl enable --now backend.service

sed -i \
    's#/run/backend/missing.sock#/run/backend/backend.sock#' \
    /etc/nginx/sites-available/backend

nginx -t

systemctl restart nginx.service

for _ in $(seq 1 15); do
    if curl -fsS http://127.0.0.1/health >/dev/null; then
        exit 0
    fi
    sleep 1
done

echo "Backend health check failed" >&2
exit 1
