import hashlib
import subprocess
from pathlib import Path

APP = Path("/app")
CONFIG_DIR = APP / "configs"
BUILD_DIR = APP / "build"
ARTIFACT_DIR = APP / "artifacts"
REPORT_DIR = APP / "reports"

BUILD = APP / "scripts" / "build.sh"
BENCHMARK = APP / "scripts" / "benchmark.sh"
VALIDATE = APP / "scripts" / "validate.sh"
RESOLVER = APP / "scripts" / "resolve_config.py"

PROTECTED = {
    "BUILD_TYPE",
    "OPT_LEVEL",
    "FAST_MATH",
    "VECTOR_WIDTH",
    "DEBUG_SYMBOLS",
    "LTO",
    "ARTIFACT_MODE",
}

EXPECTED = {
    "BUILD_TYPE": "Release",
    "OPT_LEVEL": "3",
    "FAST_MATH": "1",
    "VECTOR_WIDTH": "4",
    "DEBUG_SYMBOLS": "0",
    "LTO": "1",
    "ARTIFACT_MODE": "optimized",
}


def run(*args, check=True):
    return subprocess.run(args, cwd=APP, text=True, capture_output=True, check=check)


def parse(path):
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def reset():
    for path in (
        BUILD_DIR / "resolved_config.txt",
        BUILD_DIR / "effective_config.txt",
        ARTIFACT_DIR / "kernel_build.artifact",
        REPORT_DIR / "benchmark.txt",
    ):
        path.unlink(missing_ok=True)


def test_structure_and_no_test_modification():
    for path in (BUILD, BENCHMARK, VALIDATE, RESOLVER):
        assert path.exists()
    assert "pytest" not in RESOLVER.read_text()


def test_build_restores_release_contract():
    reset()
    run(str(BUILD))
    effective = parse(BUILD_DIR / "effective_config.txt")
    assert {k: effective.get(k) for k in EXPECTED} == EXPECTED
    assert effective["BUILD_CACHE"] == "/tmp/legacy-cache"
    assert effective["LOCAL_DIAGNOSTIC"] == "compact"


def test_artifact_provenance_matches_contract():
    run(str(BUILD))
    effective = parse(BUILD_DIR / "effective_config.txt")
    artifact = parse(ARTIFACT_DIR / "kernel_build.artifact")
    canonical = "".join(f"{k}={effective[k]}\n" for k in (
        "BUILD_TYPE","OPT_LEVEL","FAST_MATH","VECTOR_WIDTH","DEBUG_SYMBOLS","LTO","ARTIFACT_MODE"
    ))
    assert artifact["CONFIG_SHA256"] == hashlib.sha256(canonical.encode()).hexdigest()
    for key in EXPECTED:
        assert artifact[key] == EXPECTED[key]


def test_legacy_override_cannot_replace_protected_fields():
    override = CONFIG_DIR / "local.override"
    original = override.read_text()
    try:
        override.write_text(
            "OPT_LEVEL=0\nFAST_MATH=0\nVECTOR_WIDTH=1\nLTO=0\n"
            "BUILD_CACHE=/tmp/test-cache\nLOCAL_DIAGNOSTIC=full\n"
        )
        run(str(BUILD))
        effective = parse(BUILD_DIR / "effective_config.txt")
        for key, value in EXPECTED.items():
            assert effective[key] == value
        assert effective["BUILD_CACHE"] == "/tmp/test-cache"
        assert effective["LOCAL_DIAGNOSTIC"] == "full"
    finally:
        override.write_text(original)


def test_benchmark_passes_after_build():
    run(str(BUILD))
    result = run(str(BENCHMARK))
    report = parse(REPORT_DIR / "benchmark.txt")
    assert result.returncode == 0
    assert report["SCORE"] == "100"
    assert report["STATUS"] == "PASS"


def test_benchmark_rejects_stale_artifact():
    run(str(BUILD))
    effective = BUILD_DIR / "effective_config.txt"
    original = effective.read_text()
    try:
        effective.write_text(original.replace("OPT_LEVEL=3", "OPT_LEVEL=2"))
        result = run(str(BENCHMARK), check=False)
        report = parse(REPORT_DIR / "benchmark.txt")
        assert result.returncode != 0
        assert report["STATUS"] == "REGRESSION"
    finally:
        effective.write_text(original)


def test_benchmark_rejects_tampered_digest():
    run(str(BUILD))
    artifact = ARTIFACT_DIR / "kernel_build.artifact"
    original = artifact.read_text()
    try:
        artifact.write_text(original.replace("OPT_LEVEL=3", "OPT_LEVEL=4"))
        result = run(str(BENCHMARK), check=False)
        assert result.returncode != 0
        assert parse(REPORT_DIR / "benchmark.txt")["STATUS"] == "REGRESSION"
    finally:
        artifact.write_text(original)


def test_benchmark_rejects_self_consistent_wrong_artifact():
    run(str(BUILD))
    artifact = parse(ARTIFACT_DIR / "kernel_build.artifact")
    artifact["OPT_LEVEL"] = "2"
    canonical = "".join(f"{k}={artifact[k]}\n" for k in (
        "BUILD_TYPE","OPT_LEVEL","FAST_MATH","VECTOR_WIDTH","DEBUG_SYMBOLS","LTO","ARTIFACT_MODE"
    ))
    artifact["CONFIG_SHA256"] = hashlib.sha256(canonical.encode()).hexdigest()
    path = ARTIFACT_DIR / "kernel_build.artifact"
    path.write_text("GPU_KERNEL_BUILD_ARTIFACT\nFORMAT_VERSION=2\n" + "".join(f"{k}={v}\n" for k,v in artifact.items()))
    result = run(str(BENCHMARK), check=False)
    assert result.returncode != 0


def test_validation_is_end_to_end():
    reset()
    result = run(str(VALIDATE))
    assert result.returncode == 0
    assert "VALIDATION=PASS" in result.stdout


def test_resolver_does_not_embed_test_specific_answers():
    source = RESOLVER.read_text()
    assert "LOCAL_DIAGNOSTIC" not in source
    assert "/tmp/test-cache" not in source
    assert "OPT_LEVEL=3" not in source
    assert "FAST_MATH=1" not in source


def test_normal_workflow_does_not_require_network():
    assert "curl" not in (APP / "scripts" / "build.sh").read_text()
    assert "pip install" not in (APP / "scripts" / "build.sh").read_text()
