from __future__ import annotations

from pathlib import Path

from scripts.validate_task_metadata import (
    task_directories,
    validate_task_metadata,
)


def write_task(
    task_dir: Path,
    *,
    task_section: str | None = None,
    metadata_section: str = "",
    verifier_timeout: str = "600",
    agent_timeout: str = "600",
    environment_section: str = "",
) -> None:
    task_dir.mkdir(parents=True)

    if task_section is None:
        task_section = """
[task]
name = "example-task"
description = "Example benchmark task."
authors = ["Mohamed Ahmed"]
"""

    content = (
        task_section
        + metadata_section
        + f"""
[verifier]
timeout_sec = {verifier_timeout}

[agent]
timeout_sec = {agent_timeout}
"""
        + environment_section
    )

    (task_dir / "task.toml").write_text(
        content,
        encoding="utf-8",
    )


def test_valid_task_metadata_passes(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(task_dir)

    assert validate_task_metadata(task_dir) == []


def test_schema_version_without_task_section_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    task_dir.mkdir(parents=True)

    (task_dir / "task.toml").write_text(
        """
schema_version = "1.3"

[metadata]
author_name = "Test Author"
author_email = "test@example.com"
""",
        encoding="utf-8",
    )

    errors = validate_task_metadata(task_dir)

    assert errors



def test_empty_task_name_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        task_section="""
[task]
name = ""
description = "Example benchmark task."
authors = ["Mohamed Ahmed"]
""",
    )

    errors = validate_task_metadata(task_dir)

    assert any("task.name" in error for error in errors)


def test_empty_task_description_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        task_section="""
[task]
name = "example-task"
description = ""
authors = ["Mohamed Ahmed"]
""",
    )

    errors = validate_task_metadata(task_dir)

    assert any("task.description" in error for error in errors)


def test_metadata_author_name_is_accepted(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        task_section="""
[task]
name = "example-task"
description = "Example benchmark task."
""",
        metadata_section="""
[metadata]
author_name = "Mohamed Ahmed"
""",
    )

    assert validate_task_metadata(task_dir) == []


def test_missing_author_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        task_section="""
[task]
name = "example-task"
description = "Example benchmark task."
""",
    )

    errors = validate_task_metadata(task_dir)

    assert any("missing author information" in error for error in errors)


def test_invalid_verifier_timeout_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        verifier_timeout="0",
    )

    errors = validate_task_metadata(task_dir)

    assert any("verifier.timeout_sec" in error for error in errors)


def test_invalid_agent_timeout_is_flagged(tmp_path: Path) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        agent_timeout="-1",
    )

    errors = validate_task_metadata(task_dir)

    assert any("agent.timeout_sec" in error for error in errors)


def test_invalid_environment_resources_are_flagged(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "task"

    write_task(
        task_dir,
        environment_section="""
[environment]
cpus = 0
memory_mb = -1
storage_mb = 0
gpus = -1
""",
    )

    errors = validate_task_metadata(task_dir)

    assert len(errors) == 4


def test_task_directories_discovers_nested_tasks(tmp_path: Path) -> None:
    first = tmp_path / "one"
    second = tmp_path / "nested" / "two"

    first.mkdir(parents=True)
    second.mkdir(parents=True)

    (first / "task.toml").write_text("", encoding="utf-8")
    (second / "task.toml").write_text("", encoding="utf-8")

    discovered = task_directories(tmp_path)

    assert discovered == sorted(
        [first, second],
        key=lambda path: str(path),
    )


def test_valid_legacy_task_metadata_passes(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "legacy-task"
    task_dir.mkdir()

    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[metadata]
author_name = "Mohamed Ahmed"

[verifier]
timeout_sec = 180

[agent]
timeout_sec = 180

[environment]
build_timeout_sec = 600
cpus = 2
memory_mb = 2048
storage_mb = 10240
gpus = 0
""",
        encoding="utf-8",
    )

    assert validate_task_metadata(task_dir) == []


def test_legacy_task_requires_version(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "legacy-task"
    task_dir.mkdir()

    (task_dir / "task.toml").write_text(
        """
[metadata]
author_name = "Mohamed Ahmed"

[verifier]
timeout_sec = 180

[agent]
timeout_sec = 180
""",
        encoding="utf-8",
    )

    errors = validate_task_metadata(task_dir)

    assert any("legacy task must define" in error for error in errors)


def test_legacy_task_requires_author_name(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "legacy-task"
    task_dir.mkdir()

    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[metadata]

[verifier]
timeout_sec = 180

[agent]
timeout_sec = 180
""",
        encoding="utf-8",
    )

    errors = validate_task_metadata(task_dir)

    assert any("metadata.author_name" in error for error in errors)


def test_legacy_task_requires_metadata_section(
    tmp_path: Path,
) -> None:
    task_dir = tmp_path / "legacy-task"
    task_dir.mkdir()

    (task_dir / "task.toml").write_text(
        """
version = "1.0"

[verifier]
timeout_sec = 180

[agent]
timeout_sec = 180
""",
        encoding="utf-8",
    )

    errors = validate_task_metadata(task_dir)

    assert any("legacy task missing [metadata]" in error for error in errors)
