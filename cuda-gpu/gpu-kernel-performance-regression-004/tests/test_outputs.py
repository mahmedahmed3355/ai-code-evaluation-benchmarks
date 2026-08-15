from pathlib import Path
import subprocess


ROOT = Path("/app")
SCRIPTS = ROOT / "scripts"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"
PLAN = ROOT / "build" / "execution_plan.txt"
REPORT = ROOT / "reports" / "benchmark.txt"


def run_script(name: str):
    return subprocess.run(
        [str(SCRIPTS / name)],
        text=True,
        capture_output=True,
    )


def parse_key_values(path: Path):
    values = {}

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key] = value

    return values


def test_build_produces_artifact():
    result = run_script("build.sh")

    assert result.returncode == 0, result.stdout + result.stderr
    assert ARTIFACT.exists()
    assert ARTIFACT.stat().st_size > 0


def test_execution_plan_contains_all_supported_workloads():
    assert PLAN.exists()

    plan = parse_key_values(PLAN)

    assert plan["WORKLOAD_1_INPUT_SIZE"] == "4096"
    assert plan["WORKLOAD_2_INPUT_SIZE"] == "65536"
    assert plan["WORKLOAD_3_INPUT_SIZE"] == "1048576"

    assert int(plan["WORKLOAD_1_WORK_UNITS"]) > 0
    assert int(plan["WORKLOAD_2_WORK_UNITS"]) > 0
    assert int(plan["WORKLOAD_3_WORK_UNITS"]) > 0


def test_artifact_matches_execution_plan():
    artifact = parse_key_values(ARTIFACT)
    plan = parse_key_values(PLAN)

    assert artifact["TOTAL_WORK_UNITS"] == plan["TOTAL_WORK_UNITS"]

    for index in range(1, 4):
        assert (
            artifact[f"WORKLOAD_{index}_INPUT_SIZE"]
            == plan[f"WORKLOAD_{index}_INPUT_SIZE"]
        )

        assert (
            artifact[f"WORKLOAD_{index}_WORK_UNITS"]
            == plan[f"WORKLOAD_{index}_WORK_UNITS"]
        )


def test_final_configuration_uses_performance_contract():
    result = run_script("build.sh")

    assert result.returncode == 0, result.stdout + result.stderr

    config = parse_key_values(
        ROOT / "build" / "resolved_config.txt"
    )

    assert config["STRATEGY"] == "blocked"
    assert config["BLOCK_SIZE"] == "256"
    assert config["CHUNK_SIZE"] == "4096"
    assert config["VECTOR_WIDTH"] == "4"
    assert config["FAST_PATH"] == "1"
    assert config["WORK_UNIT_COST"] == "1"


def test_final_plan_is_within_performance_budget():
    plan = parse_key_values(PLAN)

    total_work = int(plan["TOTAL_WORK_UNITS"])

    assert total_work <= 500000


def test_final_validation_passes():
    result = run_script("validate.sh")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "STATUS=PASS" in result.stdout
    assert "VALIDATION=PASS" in result.stdout

def test_benchmark_rejects_over_budget_artifact():
    artifact_values = parse_key_values(ARTIFACT)

    artifact_values["STRATEGY"] = "scalar"
    artifact_values["BLOCK_SIZE"] = "64"
    artifact_values["CHUNK_SIZE"] = "256"
    artifact_values["VECTOR_WIDTH"] = "1"
    artifact_values["FAST_PATH"] = "0"
    artifact_values["WORK_UNIT_COST"] = "8"

    input_sizes = [4096, 65536, 1048576]

    total_work = 0

    for input_size in input_sizes:
        blocks = (input_size + 64 - 1) // 64
        chunks = (input_size + 256 - 1) // 256

        total_work += blocks * chunks * 4 * 2 * 8

    artifact_values["TOTAL_WORK_UNITS"] = str(total_work)

    ARTIFACT.write_text(
        "\n".join(
            f"{key}={value}"
            for key, value in artifact_values.items()
        )
        + "\n"
    )

    result = run_script("benchmark.sh")

    assert result.returncode != 0
    assert "STATUS=REGRESSION" in result.stdout

    report = parse_key_values(REPORT)

    assert report["STATUS"] == "REGRESSION"
    assert int(report["TOTAL_WORK_UNITS"]) > int(
        report["PERFORMANCE_BUDGET"]
    )

def test_artifact_cannot_claim_optimized_strategy_with_bad_work():
    artifact = parse_key_values(ARTIFACT)

    if artifact["STRATEGY"] == "blocked":
        assert int(artifact["VECTOR_WIDTH"]) == 4
        assert int(artifact["FAST_PATH"]) == 1
        assert int(artifact["WORK_UNIT_COST"]) == 1


def test_diagnostic_exposes_configuration_provenance():
    result = run_script("diagnose.py")

    assert result.returncode == 0

    output = result.stdout

    assert "[Configuration sources]" in output
    assert "[Configuration provenance]" in output
    assert "[Effective configuration]" in output
    assert "[Execution plan]" in output
    assert "[Generated artifact]" in output
    assert "[Benchmark report]" in output
