from pathlib import Path
import json,re
ROOT=Path("/app/service")
def text(): return (ROOT/"Dockerfile").read_text()
def test_01_non_root():
    t=text(); assert re.search(r"(?im)^USER\\s+(?:[1-9][0-9]{4,})(?::[1-9][0-9]{4,})?\\s*$",t)
def test_02_no_root():
    t=text().lower(); assert "user root" not in t and "sudo" not in t and " su " not in t
def test_03_no_latest():
    assert not re.search(r"(?i)^from\\s+[^\\s:]+:latest",text(),re.M)
def test_04_healthcheck():
    assert re.search(r"(?i)^healthcheck\\b",text(),re.M)
def test_05_no_secret_copy():
    t=text().lower(); assert "secrets" not in t and ".env.production" not in t and "private.key" not in t
def test_06_policy():
    p=json.loads((ROOT/"runtime-policy.json").read_text())
    assert p["read_only_rootfs"] is True and p["no_new_privileges"] is True
    assert p["capabilities_drop"]==["ALL"] and p["privileged"] is False
def test_07_tmpfs(): assert "/tmp" in json.loads((ROOT/"runtime-policy.json").read_text())["tmpfs"]
def test_08_no_host_namespaces():
    p=json.loads((ROOT/"runtime-policy.json").read_text()); assert p["network_mode"]!="host" and p["pid_mode"]!="host" and p["ipc_mode"]!="host"
def test_09_no_app_change(): assert (ROOT/"app.py").read_text().startswith("from http.server")
def test_10_no_wildcard777(): assert "chmod -R 777" not in text()
def test_11_version_externalized(): assert "DATABASE_PASSWORD" not in text() and "API_TOKEN" not in text()
