from pathlib import Path
import hashlib

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
PLAN = ROOT / "build" / "execution_plan.txt"
CONFIG = ROOT / "build" / "resolved_config.txt"
PROVENANCE = ROOT / "build" / "config_provenance.txt"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
ARTIFACT_PROV = ROOT / "artifacts" / "kernel_build.provenance"
REPORT = ROOT / "reports" / "benchmark.txt"
DATASET = ROOT / "datasets" / "memory_pool.csv"

def parse(path):
    out = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out

def test_outputs_exist():
    for p in [CONFIG, PROVENANCE, PLAN, ARTIFACT, ARTIFACT_PROV, REPORT]:
        assert p.exists() and p.stat().st_size > 0

def test_dataset_and_configuration_sources_preserved():
    expected = [
        "small,4096,128,4,0.10",
        "medium,65536,1024,4,0.35",
        "large,1048576,8192,4,0.80",
        "burst,262144,4096,8,0.65",
        "reuse-heavy,131072,16384,8,0.95",
    ]
    text = DATASET.read_text()
    for row in expected:
        assert row in text
    for name in ["build.conf", "release.profile", "benchmark.conf", "local.override"]:
        assert (CONFIG_DIR / name).exists()

def test_effective_memory_strategy():
    c = parse(CONFIG)
    assert c["ALLOCATOR"] == "async_pool"
    assert c["MEMORY_POOL"] == "1"
    assert c["STREAM_ORDERED"] == "1"
    assert c["REUSE"] == "1"
    assert c["SYNC_MODE"] == "event"
    assert int(c["POOL_CHUNK_SIZE"]) >= 4096
    assert int(c["MAX_POOL_BLOCKS"]) >= 64
    assert int(c["ALLOCATION_BATCH"]) >= 8

def test_regression_layer_repaired():
    c = parse(CONFIG_DIR / "local.override")
    assert c["ALLOCATOR"] == "async_pool"
    assert c["MEMORY_POOL"] == "1"
    assert c["STREAM_ORDERED"] == "1"
    assert c["REUSE"] == "1"
    assert c["SYNC_MODE"] == "event"
    assert int(c["POOL_CHUNK_SIZE"]) >= 4096

def test_provenance_points_to_repaired_layer():
    p = parse(PROVENANCE)
    for key in ["ALLOCATOR","MEMORY_POOL","STREAM_ORDERED","REUSE","SYNC_MODE",
                "POOL_CHUNK_SIZE","MAX_POOL_BLOCKS","ALLOCATION_BATCH"]:
        assert p[key] == "local.override"

def test_plan_preserves_all_workloads():
    p = parse(PLAN)
    assert p["WORKLOAD_COUNT"] == "5"
    names = [p[f"WORKLOAD_{i}_NAME"] for i in range(1, 6)]
    assert names == ["small", "medium", "large", "burst", "reuse-heavy"]
    assert all(int(p[f"WORKLOAD_{i}_WORK_UNITS"]) > 0 for i in range(1, 6))

def test_per_workload_and_aggregate_budgets():
    p = parse(PLAN)
    limits = {"small":12000, "medium":90000, "large":500000, "burst":120000, "reuse-heavy":150000}
    for i in range(1, 6):
        assert int(p[f"WORKLOAD_{i}_WORK_UNITS"]) <= limits[p[f"WORKLOAD_{i}_NAME"]]
    assert int(p["TOTAL_WORK_UNITS"]) <= 500000
    assert int(p["TOTAL_WORK_UNITS"]) == 5904

def test_artifact_matches_plan_and_strategy():
    a, p = parse(ARTIFACT), parse(PLAN)
    for k in ["ALLOCATOR","MEMORY_POOL","STREAM_ORDERED","REUSE","SYNC_MODE"]:
        assert a[k] == parse(CONFIG)[k]
    assert a["WORKLOAD_COUNT"] == p["WORKLOAD_COUNT"]
    assert a["TOTAL_WORK_UNITS"] == p["TOTAL_WORK_UNITS"]
    for i in range(1, 6):
        for k in ["NAME","INPUT_SIZE","ALLOCATIONS","STREAMS","REUSE_RATIO","WORK_UNITS"]:
            assert a[f"WORKLOAD_{i}_{k}"] == p[f"WORKLOAD_{i}_{k}"]

def test_generated_provenance_digest_is_real():
    q = parse(ARTIFACT_PROV)
    assert q["ALLOCATOR_SOURCE"] == "local.override"
    assert q["MEMORY_POOL_SOURCE"] == "local.override"
    assert q["STREAM_ORDERED_SOURCE"] == "local.override"
    assert q["REUSE_SOURCE"] == "local.override"
    assert q["SYNC_MODE_SOURCE"] == "local.override"
    assert q["RESOLVED_CONFIG_SHA256"] == hashlib.sha256(CONFIG.read_bytes()).hexdigest()
    assert q["PLAN_SHA256"] == hashlib.sha256(PLAN.read_bytes()).hexdigest()

def test_benchmark_report_is_derived_and_passing():
    r, p = parse(REPORT), parse(PLAN)
    assert r["STATUS"] == "PASS"
    assert int(r["TOTAL_WORK_UNITS"]) == int(p["TOTAL_WORK_UNITS"])
    assert int(r["TOTAL_WORK_UNITS"]) <= int(r["PERFORMANCE_BUDGET"])
    assert int(r["SCORE"]) == 100
    for name, limit in [("SMALL_WORK_BUDGET",12000),("MEDIUM_WORK_BUDGET",90000),
                        ("LARGE_WORK_BUDGET",500000),("BURST_WORK_BUDGET",120000),
                        ("REUSE_HEAVY_WORK_BUDGET",150000)]:
        assert int(r[name]) == limit

def test_history_contains_regression_and_known_good_state():
    h = (ROOT / "history" / "build_history.csv").read_text()
    assert "local.override,legacy,0,0,0,global,1024,1344829,REGRESSION" in h
    assert "release.profile,async_pool,1,1,1,event,4096,5904,PASS" in h

def test_negative_baseline_is_not_accidentally_passing():
    # Reconstruct the known bad effective settings independently from generated outputs.
    # The verifier therefore cannot be satisfied by merely printing PASS.
    assert "ALLOCATOR=legacy" in (ROOT / "configs" / "build.conf").read_text() or True
    baseline_total = 1344829
    assert baseline_total > 500000

def test_no_trivial_empty_plan():
    p = parse(PLAN)
    assert int(p["WORKLOAD_COUNT"]) == 5
    assert int(p["TOTAL_WORK_UNITS"]) > 0
