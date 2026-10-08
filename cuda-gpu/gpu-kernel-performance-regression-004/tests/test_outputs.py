import hashlib
import math
import subprocess
from pathlib import Path

ROOT = Path("/app")
CONFIGS = ROOT / "configs"
SCRIPTS = ROOT / "scripts"
BUILD = ROOT / "build"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
PLAN = BUILD / "execution_plan.txt"

PROTECTED = {
    "PROFILE": "release",
    "OPT_PROFILE": "release",
    "OPT_LEVEL": "3",
    "STRATEGY": "blocked",
    "BLOCK_SIZE": "256",
    "CHUNK_SIZE": "4096",
    "VECTOR_WIDTH": "4",
    "FAST_PATH": "1",
    "WORK_UNIT_COST": "1",
    "MAX_WORK_UNITS": "500000",
    "DEBUG_SYMBOLS": "0",
    "LTO": "1",
    "ARTIFACT_MODE": "optimized",
}

def run(name):
    return subprocess.run([str(SCRIPTS / name)], text=True, capture_output=True)

def parse(path):
    values = {}
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def expected_work(size):
    return math.ceil(size / 4096)

def test_build_creates_outputs():
    result = run("build.sh")
    assert result.returncode == 0, result.stdout + result.stderr
    assert ARTIFACT.exists()
    assert PLAN.exists()

def test_release_contract_and_local_diagnostics():
    config = parse(BUILD / "resolved_config.txt")
    for key, value in PROTECTED.items():
        assert config[key] == value
    assert config["DIAGNOSTIC_MODE"] == "1"
    assert config["DIAGNOSTIC_LABEL"] == "legacy-local"

def test_supported_workloads_and_budgets():
    plan = parse(PLAN)
    sizes = [4096, 65536, 1048576]
    profiles = ["balanced", "balanced", "release"]
    budgets = [12000, 90000, 500000]
    total = 0
    for index, (size, profile, budget) in enumerate(zip(sizes, profiles, budgets), 1):
        assert int(plan[f"WORKLOAD_{index}_INPUT_SIZE"]) == size
        assert plan[f"WORKLOAD_{index}_PROFILE"] == profile
        work = int(plan[f"WORKLOAD_{index}_WORK_UNITS"])
        assert work == expected_work(size)
        assert work <= budget
        total += work
    assert int(plan["TOTAL_WORK_UNITS"]) == total
    assert total <= 500000

def test_artifact_provenance():
    artifact = parse(ARTIFACT)
    plan = parse(PLAN)
    assert artifact["CONFIG_SHA256"] == digest(BUILD / "resolved_config.txt")
    assert artifact["PLAN_SHA256"] == digest(PLAN)
    assert artifact["TOTAL_WORK_UNITS"] == plan["TOTAL_WORK_UNITS"]
    for index in range(1, 4):
        assert artifact[f"WORKLOAD_{index}_INPUT_SIZE"] == plan[f"WORKLOAD_{index}_INPUT_SIZE"]
        assert artifact[f"WORKLOAD_{index}_WORK_UNITS"] == plan[f"WORKLOAD_{index}_WORK_UNITS"]

def test_complete_validation():
    result = run("validate.sh")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "VALIDATION=PASS" in result.stdout

def test_tampered_artifact_is_rejected():
    run("build.sh")
    artifact = parse(ARTIFACT)
    artifact["TOTAL_WORK_UNITS"] = "1"
    ARTIFACT.write_text("\n".join(f"{key}={value}" for key, value in artifact.items()) + "\n")
    result = run("benchmark.sh")
    assert result.returncode != 0
    assert "artifact" in result.stderr.lower()

def test_over_budget_artifact_is_rejected():
    run("build.sh")
    artifact = parse(ARTIFACT)
    artifact["TOTAL_WORK_UNITS"] = "500001"
    ARTIFACT.write_text("\n".join(f"{key}={value}" for key, value in artifact.items()) + "\n")
    result = run("benchmark.sh")
    assert result.returncode != 0

def test_diagnostic_evidence_is_available():
    result = run("diagnose.py")
    assert result.returncode == 0
    assert "[Configuration provenance]" in result.stdout
    assert "[Build history]" in result.stdout
    assert "4311810048" in result.stdout
    assert "legacy-local" in result.stdout

def test_local_override_contains_conflicting_legacy_values():
    local = parse(CONFIGS / "local.override")
    release = parse(CONFIGS / "release.profile")
    for key in ["STRATEGY", "BLOCK_SIZE", "CHUNK_SIZE", "VECTOR_WIDTH", "FAST_PATH", "WORK_UNIT_COST"]:
        assert local[key] != release[key]

def test_benchmark_contract_is_unchanged():
    contract = parse(CONFIGS / "benchmark.conf")
    assert contract["REQUIRED_PROFILE"] == "release"
    assert int(contract["SMALL_WORK_BUDGET"]) == 12000
    assert int(contract["MEDIUM_WORK_BUDGET"]) == 90000
    assert int(contract["LARGE_WORK_BUDGET"]) == 500000
    assert int(contract["AGGREGATE_WORK_BUDGET"]) == 500000
