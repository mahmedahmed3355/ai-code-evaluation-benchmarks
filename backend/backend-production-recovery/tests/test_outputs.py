import json
import os
import stat
import subprocess
import urllib.request


def run(command):
    return subprocess.run(command, shell=True, text=True, capture_output=True, timeout=30)


def get(path):
    with urllib.request.urlopen(f"http://127.0.0.1{path}", timeout=5) as r:
        return r.status, json.loads(r.read().decode())


def test_backend_active_and_enabled():
    assert run("systemctl is-active backend.service").stdout.strip() == "active"
    assert run("systemctl is-enabled backend.service").stdout.strip() == "enabled"


def test_backend_runs_as_backend_user():
    result = run("systemctl show -p User --value backend.service")
    assert result.stdout.strip() == "backend"


def test_environment_is_loaded():
    status, body = get("/api/v1/runtime")
    assert status == 200
    assert body["boot_id"] == "production"


def test_socket_contract():
    path = "/run/backend/orders.sock"
    assert os.path.exists(path)
    mode = os.stat(path).st_mode
    assert stat.S_ISSOCK(mode)
    assert (mode & 0o007) == 0
    assert (mode & 0o060) != 0
    assert run("test -S /run/backend/wrong.sock").returncode != 0


def test_nginx_is_active_and_valid():
    assert run("systemctl is-active nginx.service").stdout.strip() == "active"
    assert run("nginx -t").returncode == 0


def test_health_and_readiness_through_proxy():
    status, body = get("/health")
    assert status == 200
    assert body == {"status": "ok", "service": "orders-api"}
    status, body = get("/ready")
    assert status == 200
    assert body["ready"] is True


def test_api_path_and_data_are_preserved():
    status, body = get("/api/v1/orders/A-100")
    assert status == 200
    assert body == {"order_id": "A-100", "status": "paid", "total": 1250}
    status, body = get("/api/v1/orders/B-200")
    assert status == 200
    assert body == {"order_id": "B-200", "status": "processing", "total": 980}


def test_unknown_order_remains_404():
    try:
        urllib.request.urlopen("http://127.0.0.1/api/v1/orders/UNKNOWN", timeout=5)
        assert False
    except urllib.error.HTTPError as exc:
        assert exc.code == 404


def test_direct_backend_is_not_exposed_on_tcp():
    assert run("ss -lnt | grep -E ':8000|:8001' ").returncode != 0


def test_backend_restart_does_not_require_nginx_restart():
    before = run("systemctl show -p ActiveEnterTimestampMonotonic --value nginx.service").stdout.strip()
    assert run("systemctl restart backend.service").returncode == 0
    status, body = get("/api/v1/orders/A-100")
    assert status == 200 and body["status"] == "paid"
    after = run("systemctl show -p ActiveEnterTimestampMonotonic --value nginx.service").stdout.strip()
    assert before == after


def test_repeated_restart_recovery():
    for _ in range(2):
        assert run("systemctl restart backend.service").returncode == 0
        status, body = get("/health")
        assert status == 200 and body["status"] == "ok"
        status, body = get("/api/v1/orders/B-200")
        assert status == 200 and body["order_id"] == "B-200"
