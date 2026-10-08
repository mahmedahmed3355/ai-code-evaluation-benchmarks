import json
import os
import socket
import stat
import subprocess
import urllib.request


def run(command):
    return subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
    )


def http(path="/", headers=None):
    request = urllib.request.Request(
        f"http://127.0.0.1{path}",
        headers=headers or {},
    )
    return urllib.request.urlopen(request, timeout=5)


def test_backend_service_active_and_enabled():
    active = run("systemctl is-active backend.service")
    enabled = run("systemctl is-enabled backend.service")
    assert active.returncode == 0
    assert active.stdout.strip() == "active"
    assert enabled.returncode == 0
    assert enabled.stdout.strip() == "enabled"


def test_backend_socket_is_unix_socket():
    path = "/run/backend/backend.sock"
    assert os.path.exists(path)
    assert stat.S_ISSOCK(os.stat(path).st_mode)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(2)
    sock.connect(path)
    sock.close()


def test_gunicorn_is_using_expected_socket():
    result = run("ss -lx")
    assert result.returncode == 0
    assert "/run/backend/backend.sock" in result.stdout


def test_nginx_active_and_valid():
    active = run("systemctl is-active nginx.service")
    assert active.returncode == 0
    assert active.stdout.strip() == "active"

    config = run("nginx -t")
    assert config.returncode == 0


def test_nginx_is_really_proxying_health():
    response = http("/health")
    assert response.status == 200
    body = json.loads(response.read().decode())
    assert body == {"status": "ok"}


def test_root_response_is_preserved():
    response = http("/")
    assert response.status == 200
    body = json.loads(response.read().decode())
    assert body == {"service": "backend", "status": "running"}


def test_forwarded_headers_are_configured():
    config = open("/etc/nginx/sites-available/backend").read()
    assert "proxy_set_header Host $host;" in config
    assert "proxy_set_header X-Real-IP $remote_addr;" in config
    assert "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;" in config


def test_backend_logs_are_configured():
    unit = open("/etc/systemd/system/backend.service").read()
    nginx = open("/etc/nginx/sites-available/backend").read()
    assert "--access-logfile /var/log/backend/access.log" in unit
    assert "--error-logfile /var/log/backend/error.log" in unit
    assert "access_log /var/log/nginx/backend_access.log;" in nginx
    assert "error_log /var/log/nginx/backend_error.log;" in nginx


def test_nginx_does_not_bypass_socket():
    config = open("/etc/nginx/sites-available/backend").read()
    assert "proxy_pass http://unix:/run/backend/backend.sock:;" in config
    assert "proxy_pass http://127.0.0.1:" not in config
    assert "proxy_pass http://localhost:" not in config


def test_backend_restart_recreates_socket_and_proxy_stays_healthy():
    result = run("systemctl restart backend.service")
    assert result.returncode == 0

    active = run("systemctl is-active backend.service")
    assert active.returncode == 0
    assert active.stdout.strip() == "active"

    for _ in range(20):
        try:
            response = http("/health")
            if response.status == 200:
                body = json.loads(response.read().decode())
                if body == {"status": "ok"}:
                    break
        except Exception:
            pass
        import time
        time.sleep(0.25)
    else:
        raise AssertionError("backend did not recover through Nginx after restart")


def test_backend_unit_preserves_runtime_directory():
    unit = open("/etc/systemd/system/backend.service").read()
    assert "RuntimeDirectory=backend" in unit
    assert "RuntimeDirectoryMode=0755" in unit
    assert "unix:/run/backend/backend.sock" in unit


def test_application_code_was_not_replaced():
    app = open("/app/app.py").read()
    assert '@app.get("/health")' in app
    assert '@app.get("/")' in app
    assert 'return {"status": "ok"}' in app
    assert '"service": "backend"' in app
