import json
import os
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


def test_backend_service_active():
    result = run("systemctl is-active backend.service")

    assert result.returncode == 0
    assert result.stdout.strip() == "active"


def test_backend_socket_exists():
    socket_path = "/run/backend/backend.sock"

    assert os.path.exists(socket_path)
    assert stat.S_ISSOCK(os.stat(socket_path).st_mode)


def test_nginx_active():
    result = run("systemctl is-active nginx.service")

    assert result.returncode == 0
    assert result.stdout.strip() == "active"


def test_nginx_configuration():
    result = run("nginx -t")

    assert result.returncode == 0


def test_health_endpoint():
    response = urllib.request.urlopen(
        "http://127.0.0.1/health",
        timeout=5,
    )

    assert response.status == 200

    body = json.loads(response.read().decode())

    assert body["status"] == "ok"


def test_root_endpoint():
    response = urllib.request.urlopen(
        "http://127.0.0.1/",
        timeout=5,
    )

    assert response.status == 200

    body = json.loads(response.read().decode())

    assert body["service"] == "backend"
    assert body["status"] == "running"


def test_restart_recovery():
    result = run("systemctl restart backend.service")

    assert result.returncode == 0

    result = run("systemctl is-active backend.service")

    assert result.returncode == 0
    assert result.stdout.strip() == "active"

    response = urllib.request.urlopen(
        "http://127.0.0.1/health",
        timeout=5,
    )

    assert response.status == 200
