from pathlib import Path

ROOT = Path("/app")

CONFIG_DIR = ROOT / "configs"
DATASET = ROOT / "datasets" / "workload.csv"

ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
PLAN = ROOT / "build" / "execution_plan.txt"
REPORT = ROOT / "reports" / "benchmark.txt"


def parse_key_values(path: Path):
    values = {}

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def test_required_outputs_exist():
    """The agent must produce all required benchmark outputs."""
    assert ARTIFACT.exists()
    assert ARTIFACT.stat().st_size > 0

    assert PLAN.exists()
    assert PLAN.stat().st_size > 0

    assert REPORT.exists()
    assert REPORT.stat().st_size > 0


def test_execution_plan_preserves_all_workloads():
    """All supported workload sizes must remain represented."""
    plan = parse_key_values(PLAN)

    assert plan["WORKLOAD_1_INPUT_SIZE"] == "4096"
    assert plan["WORKLOAD_2_INPUT_SIZE"] == "65536"
    assert plan["WORKLOAD_3_INPUT_SIZE"] == "1048576"

    assert int(plan["WORKLOAD_1_WORK_UNITS"]) > 0
    assert int(plan["WORKLOAD_2_WORK_UNITS"]) > 0
    assert int(plan["WORKLOAD_3_WORK_UNITS"]) > 0


def test_artifact_matches_execution_plan():
    """The artifact must faithfully describe the generated execution plan."""
    artifact = parse_key_values(ARTIFACT)
    plan = parse_key_values(PLAN)

    assert artifact["TOTAL_WORK_UNITS"] == plan["TOTAL_WORK_UNITS"]

    for index in range(1, 4):
        assert artifact[f"WORKLOAD_{index}_INPUT_SIZE"] == plan[f"WORKLOAD_{index}_INPUT_SIZE"]

        assert artifact[f"WORKLOAD_{index}_WORK_UNITS"] == plan[f"WORKLOAD_{index}_WORK_UNITS"]


def test_final_configuration_uses_coalesced_memory_contract():
    """The effective configuration must enable the optimized access path."""
    config = parse_key_values(ROOT / "build" / "resolved_config.txt")

    assert config["BLOCK_SIZE"] == "256"
    assert config["VECTOR_WIDTH"] == "4"
    assert config["COALESCED_ACCESS"] == "1"
    assert config["ALIGNED_ACCESS"] == "1"
    assert config["FAST_PATH"] == "1"
    assert config["CHUNK_SIZE"] == "4096"


def test_final_plan_is_within_performance_budget():
    """The optimized plan must stay within the declared work budget."""
    plan = parse_key_values(PLAN)

    assert int(plan["TOTAL_WORK_UNITS"]) <= 500000


def test_final_benchmark_passes():
    """The submitted benchmark report must indicate a successful run."""
    report = parse_key_values(REPORT)

    assert report["STATUS"] == "PASS"
    assert int(report["TOTAL_WORK_UNITS"]) <= int(report["PERFORMANCE_BUDGET"])
    assert int(report["SCORE"]) == 100


def test_artifact_contains_optimized_memory_settings():
    """The generated artifact must record the optimized memory settings."""
    artifact = parse_key_values(ARTIFACT)

    assert artifact["BLOCK_SIZE"] == "256"
    assert artifact["VECTOR_WIDTH"] == "4"
    assert artifact["COALESCED_ACCESS"] == "1"
    assert artifact["ALIGNED_ACCESS"] == "1"
    assert artifact["FAST_PATH"] == "1"


def test_required_configuration_sources_exist():
    """All configuration layers needed for provenance must be preserved."""
    assert (CONFIG_DIR / "build.conf").exists()
    assert (CONFIG_DIR / "release.profile").exists()
    assert (CONFIG_DIR / "benchmark.conf").exists()
    assert (CONFIG_DIR / "local.override").exists()


def test_workload_dataset_is_preserved():
    """The original workload definitions must not be removed or rewritten."""
    text = DATASET.read_text()

    assert "small,4096,128" in text
    assert "medium,65536,64" in text
    assert "large,1048576,32" in text


def test_bad_configuration_would_exceed_budget():
    """The known regressed configuration must remain demonstrably over budget."""
    bad_config = {
        "BLOCK_SIZE": 128,
        "VECTOR_WIDTH": 1,
        "COALESCED_ACCESS": 0,
        "ALIGNED_ACCESS": 0,
        "FAST_PATH": 0,
    }

    penalty = 1

    if bad_config["COALESCED_ACCESS"] == 0:
        penalty *= 8

    if bad_config["ALIGNED_ACCESS"] == 0:
        penalty *= 4

    if bad_config["VECTOR_WIDTH"] == 1:
        penalty *= 2

    if bad_config["FAST_PATH"] == 0:
        penalty *= 2

    baseline_total = (32 + 512 + 8192) * penalty

    assert baseline_total > 500000


def test_configuration_provenance_is_preserved():
    """The configuration layers must remain independently inspectable."""
    for path in [
        CONFIG_DIR / "build.conf",
        CONFIG_DIR / "release.profile",
        CONFIG_DIR / "benchmark.conf",
        CONFIG_DIR / "local.override",
    ]:
        text = path.read_text()
        assert "=" in text
        assert len(text.strip()) > 0
