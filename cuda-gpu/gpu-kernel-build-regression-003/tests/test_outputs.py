import subprocess
from pathlib import Path

import pytest

APP = Path("/app")

CONFIG_DIR = APP / "configs"
BUILD_DIR = APP / "build"
ARTIFACT_DIR = APP / "artifacts"
REPORT_DIR = APP / "reports"

BUILD_SCRIPT = APP / "scripts" / "build.sh"
BENCHMARK_SCRIPT = APP / "scripts" / "benchmark.sh"
VALIDATE_SCRIPT = APP / "scripts" / "validate.sh"
DIAGNOSE_SCRIPT = APP / "scripts" / "diagnose.py"

BUILD_CONFIG = CONFIG_DIR / "build.conf"
RELEASE_PROFILE = CONFIG_DIR / "release.profile"
BENCHMARK_CONFIG = CONFIG_DIR / "benchmark.conf"
LOCAL_OVERRIDE = CONFIG_DIR / "local.override"

EXPECTED = {
    "BUILD_TYPE": "Release",
    "OPT_LEVEL": "3",
    "FAST_MATH": "1",
    "VECTOR_WIDTH": "4",
    "DEBUG_SYMBOLS": "0",
    "LTO": "1",
    "ARTIFACT_MODE": "optimized",
}


def run_command(*args, check=True):
    return subprocess.run(
        list(args),
        cwd=APP,
        text=True,
        capture_output=True,
        check=check,
    )


def parse_key_values(path: Path):
    values = {}

    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def clean_generated_state():
    for path in (
        BUILD_DIR / "resolved_config.txt",
        BUILD_DIR / "effective_config.txt",
        ARTIFACT_DIR / "kernel_build.artifact",
        REPORT_DIR / "benchmark.txt",
    ):
        path.unlink(missing_ok=True)


@pytest.fixture(autouse=True)
def reset_generated_state():
    clean_generated_state()
    yield


def test_repository_structure():
    required = [
        BUILD_CONFIG,
        RELEASE_PROFILE,
        BENCHMARK_CONFIG,
        LOCAL_OVERRIDE,
        BUILD_SCRIPT,
        BENCHMARK_SCRIPT,
        VALIDATE_SCRIPT,
        DIAGNOSE_SCRIPT,
    ]

    for path in required:
        assert path.exists(), f"Required repository file is missing: {path}"


def test_build_produces_artifact():
    result = run_command(
        str(BUILD_SCRIPT),
        check=True,
    )

    assert "Build completed successfully." in result.stdout

    artifact = ARTIFACT_DIR / "kernel_build.artifact"

    assert artifact.exists()
    assert artifact.stat().st_size > 0


def test_effective_configuration_matches_contract():
    run_command(str(BUILD_SCRIPT))

    effective = parse_key_values(BUILD_DIR / "effective_config.txt")

    for key, expected in EXPECTED.items():
        if key == "ARTIFACT_MODE":
            continue

        assert effective.get(key) == expected, (
            f"{key}={effective.get(key)!r}, expected {expected!r}"
        )


def test_artifact_matches_effective_configuration():
    run_command(str(BUILD_SCRIPT))

    effective = parse_key_values(BUILD_DIR / "effective_config.txt")

    artifact = parse_key_values(ARTIFACT_DIR / "kernel_build.artifact")

    for key in (
        "BUILD_TYPE",
        "OPT_LEVEL",
        "FAST_MATH",
        "VECTOR_WIDTH",
        "DEBUG_SYMBOLS",
        "LTO",
    ):
        assert artifact.get(key) == effective.get(key), f"Artifact/config mismatch for {key}"

    assert artifact.get("ARTIFACT_MODE") == EXPECTED["ARTIFACT_MODE"]


def test_benchmark_passes():
    run_command(str(BUILD_SCRIPT))

    result = run_command(
        str(BENCHMARK_SCRIPT),
        check=True,
    )

    report = parse_key_values(REPORT_DIR / "benchmark.txt")

    assert report.get("SCORE") == "100"
    assert report.get("STATUS") == "PASS"
    assert "STATUS=PASS" in result.stdout


def test_complete_validation_workflow_passes():
    result = run_command(
        str(VALIDATE_SCRIPT),
        check=True,
    )

    assert result.returncode == 0
    assert "VALIDATION=PASS" in result.stdout

    report = parse_key_values(REPORT_DIR / "benchmark.txt")

    assert report.get("SCORE") == "100"
    assert report.get("STATUS") == "PASS"


def test_legacy_override_cannot_break_contract():
    original = LOCAL_OVERRIDE.read_text()

    try:
        LOCAL_OVERRIDE.write_text(
            """# Legacy compatibility settings

OPT_LEVEL=0
FAST_MATH=0
VECTOR_WIDTH=1
LTO=0
"""
        )

        run_command(
            str(BUILD_SCRIPT),
            check=True,
        )

        effective = parse_key_values(BUILD_DIR / "effective_config.txt")

        assert effective["OPT_LEVEL"] == "3"
        assert effective["FAST_MATH"] == "1"
        assert effective["VECTOR_WIDTH"] == "4"
        assert effective["LTO"] == "1"

        run_command(
            str(BENCHMARK_SCRIPT),
            check=True,
        )

        report = parse_key_values(REPORT_DIR / "benchmark.txt")

        assert report["SCORE"] == "100"
        assert report["STATUS"] == "PASS"

    finally:
        LOCAL_OVERRIDE.write_text(original)


def test_benchmark_rejects_bad_artifact():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    bad_artifact = """GPU_KERNEL_BUILD_ARTIFACT
FORMAT_VERSION=1
CONFIG_SHA256=invalid
BUILD_TYPE=Release
OPT_LEVEL=0
FAST_MATH=0
VECTOR_WIDTH=1
DEBUG_SYMBOLS=1
LTO=0
ARTIFACT_MODE=debug
"""

    artifact = ARTIFACT_DIR / "kernel_build.artifact"
    artifact.write_text(bad_artifact)

    result = run_command(
        str(BENCHMARK_SCRIPT),
        check=False,
    )

    assert result.returncode != 0

    report = REPORT_DIR / "benchmark.txt"

    assert report.exists()

    values = parse_key_values(report)

    assert values.get("SCORE") != "100"
    assert values.get("STATUS") == "REGRESSION"


def test_validation_uses_benchmark_stage():
    source = VALIDATE_SCRIPT.read_text()

    assert "benchmark.sh" in source
    assert "VALIDATION=PASS" in source
    assert "VALIDATION=FAIL" in source


def test_diagnostic_tool_remains_operational():
    run_command(str(BUILD_SCRIPT))

    result = run_command(
        str(DIAGNOSE_SCRIPT),
        check=True,
    )

    output = result.stdout

    assert result.returncode == 0
    assert "[Configuration sources]" in output
    assert "[Configuration provenance]" in output
    assert "[Effective configuration]" in output
    assert "[Generated artifact]" in output
