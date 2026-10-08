import json
from pathlib import Path

def validate_environment(env):
    required = ["WORKER_CONFIG", "WORKER_USER", "WORKER_MEMORY_MB"]
    if any(k not in env for k in required):
        return False
    if not Path(env["WORKER_CONFIG"]).exists():
        return False
    return int(env["WORKER_MEMORY_MB"]) >= 128

def start(env):
    if not validate_environment(env):
        raise RuntimeError("configuration validation failed")
    return {"status": "started", "ready": True, "pid1": False}

def run_once(env, mode="normal"):
    if mode == "transient-failure":
        raise RuntimeError("transient worker failure")
    if mode == "clean-stop":
        return {"status": "stopped", "clean": True}
    return {"status": "running", "ready": True}
