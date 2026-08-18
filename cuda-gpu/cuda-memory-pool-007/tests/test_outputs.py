from pathlib import Path

ROOT = Path("/app")

CONFIG_DIR = ROOT / "configs"

PLAN = ROOT / "build" / "execution_plan.txt"
CONFIG = ROOT / "build" / "resolved_config.txt"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
REPORT = ROOT / "reports" / "benchmark.txt"
DATASET = ROOT / "datasets" / "memory_pool.csv"


def parse_key_values(path):
    values = {}

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def test_required_outputs_exist():
    for path in [CONFIG, PLAN, ARTIFACT, REPORT]:
        assert path.exists(), f"Missing required artifact: {path}"
        assert path.stat().st_size > 0, f"Empty artifact: {path}"


def test_all_supported_workloads_are_preserved():
    assert DATASET.exists()

    text = DATASET.read_text()

    assert "small,4096,128,4,0.10" in text
    assert "medium,65536,1024,4,0.35" in text
    assert "large,1048576,8192,4,0.80" in text
    assert "burst,262144,4096,8,0.65" in text
    assert "reuse-heavy,131072,16384,8,0.95" in text


def test_execution_plan_contains_all_workloads():
    plan = parse_key_values(PLAN)

    assert plan["WORKLOAD_COUNT"] == "5"

    for index in range(1, 6):
        assert int(plan[f"WORKLOAD_{index}_INPUT_SIZE"]) > 0
        assert int(plan[f"WORKLOAD_{index}_ALLOCATIONS"]) > 0
        assert int(plan[f"WORKLOAD_{index}_STREAMS"]) > 0
        assert int(plan[f"WORKLOAD_{index}_WORK_UNITS"]) > 0

    assert int(plan["TOTAL_WORK_UNITS"]) > 0


def test_final_configuration_uses_memory_pool_contract():
    config = parse_key_values(CONFIG)

    assert config["ALLOCATOR"] == "async_pool"
    assert config["MEMORY_POOL"] == "1"
    assert config["STREAM_ORDERED"] == "1"
    assert config["REUSE"] == "1"
    assert config["SYNC_MODE"] == "event"

    assert int(config["POOL_CHUNK_SIZE"]) >= 4096
    assert int(config["MAX_POOL_BLOCKS"]) >= 64
    assert int(config["ALLOCATION_BATCH"]) >= 8


def test_final_plan_is_within_performance_budget():
    plan = parse_key_values(PLAN)
    config = parse_key_values(CONFIG)

    total_work = int(plan["TOTAL_WORK_UNITS"])
    budget = int(config["PERFORMANCE_BUDGET"])

    assert total_work <= budget


def test_artifact_matches_execution_plan():
    artifact = parse_key_values(ARTIFACT)
    plan = parse_key_values(PLAN)

    assert artifact["WORKLOAD_COUNT"] == plan["WORKLOAD_COUNT"]
    assert artifact["TOTAL_WORK_UNITS"] == plan["TOTAL_WORK_UNITS"]

    for index in range(1, 6):
        for key in [
            "NAME",
            "INPUT_SIZE",
            "ALLOCATIONS",
            "STREAMS",
            "WORK_UNITS",
        ]:
            assert (
                artifact[f"WORKLOAD_{index}_{key}"]
                == plan[f"WORKLOAD_{index}_{key}"]
            )


def test_artifact_contains_memory_pool_settings():
    artifact = parse_key_values(ARTIFACT)

    assert artifact["ALLOCATOR"] == "async_pool"
    assert artifact["MEMORY_POOL"] == "1"
    assert artifact["STREAM_ORDERED"] == "1"
    assert artifact["REUSE"] == "1"
    assert artifact["SYNC_MODE"] == "event"


def test_benchmark_report_matches_final_state():
    report = parse_key_values(REPORT)
    plan = parse_key_values(PLAN)

    assert report["STATUS"] == "PASS"
    assert report["STATUS"] != "REGRESSION"

    assert int(report["TOTAL_WORK_UNITS"]) == int(
        plan["TOTAL_WORK_UNITS"]
    )

    assert int(report["TOTAL_WORK_UNITS"]) <= int(
        report["PERFORMANCE_BUDGET"]
    )

    assert int(report["SCORE"]) == 100


def test_required_configuration_sources_exist():
    required = [
        "build.conf",
        "release.profile",
        "benchmark.conf",
        "local.override",
    ]

    for name in required:
        path = CONFIG_DIR / name
        assert path.exists(), f"Missing configuration artifact: {name}"
        assert path.stat().st_size > 0


def test_configuration_provenance_is_preserved():
    config = parse_key_values(CONFIG)

    assert "ALLOCATOR" in config
    assert "MEMORY_POOL" in config
    assert "STREAM_ORDERED" in config
    assert "REUSE" in config
    assert "SYNC_MODE" in config


def test_configuration_is_not_satisfied_by_status_text_only():
    report = parse_key_values(REPORT)
    plan = parse_key_values(PLAN)
    artifact = parse_key_values(ARTIFACT)

    assert report["STATUS"] == "PASS"

    assert int(report["TOTAL_WORK_UNITS"]) == int(
        plan["TOTAL_WORK_UNITS"]
    )

    assert int(artifact["TOTAL_WORK_UNITS"]) == int(
        plan["TOTAL_WORK_UNITS"]
    )

    assert int(report["TOTAL_WORK_UNITS"]) <= int(
        report["PERFORMANCE_BUDGET"]
    )


def test_no_trivial_zero_workload_solution():
    plan = parse_key_values(PLAN)

    assert int(plan["WORKLOAD_COUNT"]) == 5

    total = int(plan["TOTAL_WORK_UNITS"])
    assert total > 0

    for index in range(1, 6):
        assert int(plan[f"WORKLOAD_{index}_WORK_UNITS"]) > 0

