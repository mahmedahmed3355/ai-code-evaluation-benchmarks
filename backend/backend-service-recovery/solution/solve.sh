#!/bin/bash
set -euo pipefail

# Restore the service lifecycle first so systemd owns the backend and creates
# /run/backend/backend.sock through RuntimeDirectory.
systemctl daemon-reload
systemctl enable backend.service
systemctl restart backend.service

# Restore the intended Unix-socket upstream without touching application code.
cat > /etc/nginx/sites-available/backend <<'NGINX'
server {
    listen 80 default_server;
    server_name _;

    access_log /var/log/nginx/backend_access.log;
    error_log /var/log/nginx/backend_error.log;

    location / {
        proxy_pass http://unix:/run/backend/backend.sock:;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX

nginx -t
systemctl restart nginx.service

for _ in $(seq 1 20); do
    if curl -fsS http://127.0.0.1/health | grep -q '"status":"ok"'; then
        curl -fsS http://127.0.0.1/ >/dev/null
        exit 0
    fi
    sleep 1
done

echo "Backend health check failed" >&2
systemctl status backend.service --no-pager || true
exit 1
