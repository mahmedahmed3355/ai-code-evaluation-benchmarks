from pathlib import Path

from scripts.task_manifest import validate_manifest

ROOT = Path(__file__).resolve().parents[1]


def write_manifest(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "task.toml"
    path.write_text(content, encoding="utf-8")
    return path


def valid_harbor_manifest() -> str:
    return """
version = "1.0"

[metadata]
author_name = "Test"

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 600.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
allow_internet = false
"""


def valid_schema_manifest() -> str:
    return """
schema_version = "1.1"

[task]
name = "sample task"

[metadata]
language = "en"

[verifier]
timeout_sec = 120.0

[agent]
timeout_sec = 600.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 2048
storage_mb = 10240
gpus = 0
allow_internet = true
"""


def test_valid_harbor_manifest_passes(tmp_path: Path):
    result = validate_manifest(
        write_manifest(tmp_path, valid_harbor_manifest())
    )

    assert result.valid
    assert result.errors == ()


def test_valid_schema_manifest_passes(tmp_path: Path):
    result = validate_manifest(
        write_manifest(tmp_path, valid_schema_manifest())
    )

    assert result.valid
    assert result.errors == ()


def test_manifest_without_version_is_backward_compatible(tmp_path: Path):
    content = valid_harbor_manifest().replace(
        'version = "1.0"\n\n',
        "",
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert result.valid
    assert result.errors == ()


def test_missing_required_section_is_reported(tmp_path: Path):
    content = valid_harbor_manifest().replace(
        '[agent]\ntimeout_sec = 600.0\n\n',
        "",
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "missing or invalid [agent] section" in result.errors


def test_task_name_is_required_when_task_section_exists(tmp_path: Path):
    content = valid_schema_manifest().replace(
        'name = "sample task"',
        'name = ""',
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "missing or invalid task.name" in result.errors


def test_invalid_verifier_timeout_is_reported(tmp_path: Path):
    content = valid_harbor_manifest().replace(
        "timeout_sec = 120.0",
        "timeout_sec = 0",
        1,
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "verifier.timeout_sec must be positive" in result.errors


def test_invalid_agent_timeout_is_reported(tmp_path: Path):
    content = valid_harbor_manifest().replace(
        "timeout_sec = 600.0",
        "timeout_sec = -1",
        1,
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "agent.timeout_sec must be positive" in result.errors


def test_invalid_environment_resources_are_reported(tmp_path: Path):
    content = (
        valid_harbor_manifest()
        .replace("cpus = 1", "cpus = 0")
        .replace("memory_mb = 2048", "memory_mb = -1")
        .replace("storage_mb = 10240", "storage_mb = false")
        .replace("gpus = 0", "gpus = 1.5")
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "environment.cpus must be positive" in result.errors
    assert "environment.memory_mb must be positive" in result.errors
    assert "environment.storage_mb must be positive" in result.errors
    assert "environment.gpus must be a non-negative integer" in result.errors


def test_invalid_allow_internet_type_is_reported(tmp_path: Path):
    content = valid_harbor_manifest().replace(
        "allow_internet = false",
        'allow_internet = "false"',
    )

    result = validate_manifest(write_manifest(tmp_path, content))

    assert not result.valid
    assert "environment.allow_internet must be a boolean" in result.errors


def test_invalid_toml_is_reported(tmp_path: Path):
    path = write_manifest(
        tmp_path,
        """
version = "1.0"

[metadata
author_name = "broken"
""",
    )

    result = validate_manifest(path)

    assert not result.valid
    assert len(result.errors) == 1
    assert result.errors[0].startswith("invalid TOML:")


def test_real_repository_manifests_pass_validation():
    manifests = (
        ROOT / "cuda-gpu/cuda-shared-memory-001/task.toml",
        ROOT / "cuda-gpu/cuda-stream-event-dependency/task.toml",
        ROOT / "infrastructure/kafka-consumer-offset-recovery/task.toml",
        ROOT / "backend/backend-async-job-recovery/task.toml",
        ROOT / "arabic-evaluation/arabic-count-notification/task.toml",
    )

    for manifest in manifests:
        result = validate_manifest(manifest)
        assert result.valid, f"{manifest}: {result.errors}"
