from pathlib import Path
import hashlib

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
DATASET = ROOT / "datasets" / "workload.csv"
HISTORY = ROOT / "history" / "build_history.csv"
CONFIG = ROOT / "build" / "resolved_config.txt"
PROVENANCE = ROOT / "build" / "config_provenance.txt"
PLAN = ROOT / "build" / "execution_plan.txt"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
ARTIFACT_PROV = ROOT / "artifacts" / "kernel_build.provenance"
REPORT = ROOT / "reports" / "benchmark.txt"

def parse(path):
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values

def test_outputs_exist():
    for path in [CONFIG, PROVENANCE, PLAN, ARTIFACT, ARTIFACT_PROV, REPORT]:
        assert path.exists() and path.stat().st_size > 0

def test_workloads_are_preserved():
    text = DATASET.read_text()
    assert "small,4096,128" in text
    assert "medium,65536,64" in text
    assert "large,1048576,32" in text

def test_configuration_layers_remain():
    for name in ["build.conf", "release.profile", "benchmark.conf", "local.override"]:
        assert (CONFIG_DIR / name).exists()

def test_release_contract_is_optimized():
    release = parse(CONFIG_DIR / "release.profile")
    for key, value in {
        "BLOCK_SIZE":"256",
        "VECTOR_WIDTH":"4",
        "COALESCED_ACCESS":"1",
        "ALIGNED_ACCESS":"1",
        "FAST_PATH":"1",
        "CHUNK_SIZE":"4096",
    }.items():
        assert release[key] == value

def test_regression_layer_is_repaired():
    local = parse(CONFIG_DIR / "local.override")
    release = parse(CONFIG_DIR / "release.profile")
    for key in ["BLOCK_SIZE","VECTOR_WIDTH","COALESCED_ACCESS","ALIGNED_ACCESS","FAST_PATH","CHUNK_SIZE"]:
        assert local[key] == release[key]

def test_effective_config_and_provenance():
    cfg = parse(CONFIG)
    prov = parse(PROVENANCE)
    for key in ["BLOCK_SIZE","VECTOR_WIDTH","COALESCED_ACCESS","ALIGNED_ACCESS","FAST_PATH","CHUNK_SIZE"]:
        assert cfg[key] == parse(CONFIG_DIR / "local.override")[key]
        assert prov[key] == "local.override"

def test_plan_preserves_workloads_and_budgets():
    plan = parse(PLAN)
    assert [plan[f"WORKLOAD_{i}_INPUT_SIZE"] for i in range(1,4)] == ["4096","65536","1048576"]
    assert int(plan["WORKLOAD_1_WORK_UNITS"]) <= 12000
    assert int(plan["WORKLOAD_2_WORK_UNITS"]) <= 90000
    assert int(plan["WORKLOAD_3_WORK_UNITS"]) <= 500000
    assert int(plan["TOTAL_WORK_UNITS"]) <= 500000

def test_artifact_matches_plan():
    a = parse(ARTIFACT)
    p = parse(PLAN)
    for key in ["TOTAL_WORK_UNITS"] + [f"WORKLOAD_{i}_{field}" for i in range(1,4) for field in ["NAME","INPUT_SIZE","WORK_UNITS"]]:
        assert a[key] == p[key]

def test_artifact_records_effective_memory_strategy():
    a = parse(ARTIFACT)
    for key, value in {
        "BLOCK_SIZE":"256","VECTOR_WIDTH":"4","COALESCED_ACCESS":"1",
        "ALIGNED_ACCESS":"1","FAST_PATH":"1","CHUNK_SIZE":"4096"
    }.items():
        assert a[key] == value

def test_artifact_provenance_digest():
    expected = hashlib.sha256(CONFIG.read_bytes() + PROVENANCE.read_bytes() + PLAN.read_bytes()).hexdigest()
    assert parse(ARTIFACT_PROV)["CONFIG_PLAN_SHA256"] == expected

def test_history_supports_incident_diagnosis():
    text = HISTORY.read_text()
    assert "release-2026-09-15,release.profile,4368,PASS" in text
    assert "local-2026-10-07,local.override,559104,REGRESSION" in text

def test_benchmark_passes():
    report = parse(REPORT)
    assert report["STATUS"] == "PASS"
    assert int(report["SCORE"]) == 100
    assert int(report["TOTAL_WORK_UNITS"]) <= int(report["PERFORMANCE_BUDGET"])

def test_baseline_is_a_real_regression():
    baseline = (32 + 512 + 8192) * 64
    assert baseline == 559104
    assert baseline > 500000

def test_no_benchmark_source_was_replaced():
    for rel in [
        "scripts/benchmark.sh",
        "scripts/generate_plan.py",
        "scripts/generate_artifact.py",
        "scripts/resolve_config.py",
        "scripts/validate.sh",
    ]:
        assert (ROOT / rel).exists()
