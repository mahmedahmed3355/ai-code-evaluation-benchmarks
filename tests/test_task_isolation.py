from pathlib import Path
from unittest.mock import patch

from scripts.task_isolation import (
    REQUIRED_FILES,
    check_task,
    image_tag,
    missing_assets,
)


def create_task(root: Path) -> Path:
    task = root / "category" / "sample-task"

    for relative in REQUIRED_FILES:
        path = task / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test\n", encoding="utf-8")

    return task


def test_missing_assets_accepts_complete_task(tmp_path: Path):
    task = create_task(tmp_path)

    assert missing_assets(task) == ()


def test_missing_assets_reports_missing_file(tmp_path: Path):
    task = create_task(tmp_path)

    (task / "tests" / "Dockerfile").unlink()

    missing = missing_assets(task)

    assert "tests/Dockerfile" in missing


def test_check_task_without_building_images_reports_not_attempted(tmp_path: Path):
    task = create_task(tmp_path)

    result = check_task(task, build_images=False)

    assert result.structurally_valid
    assert result.passed

    assert not result.environment.attempted
    assert result.environment.succeeded is None

    assert not result.tests.attempted
    assert result.tests.succeeded is None


def test_check_task_skips_build_when_assets_missing(tmp_path: Path):
    task = create_task(tmp_path)

    (task / "environment" / "Dockerfile").unlink()

    with patch("scripts.task_isolation.docker_build") as build:
        result = check_task(task)

    assert not result.structurally_valid
    assert not result.passed
    assert "environment/Dockerfile" in result.missing

    assert not result.environment.attempted
    assert result.environment.succeeded is None

    assert not result.tests.attempted
    assert result.tests.succeeded is None

    build.assert_not_called()


def test_check_task_records_successful_image_builds(tmp_path: Path):
    task = create_task(tmp_path)

    with patch(
        "scripts.task_isolation.docker_build",
        side_effect=[True, True],
    ) as build:
        result = check_task(task)

    assert result.structurally_valid
    assert result.passed

    assert result.environment.attempted
    assert result.environment.succeeded is True

    assert result.tests.attempted
    assert result.tests.succeeded is True

    assert build.call_count == 2


def test_check_task_records_failed_environment_build(tmp_path: Path):
    task = create_task(tmp_path)

    with patch(
        "scripts.task_isolation.docker_build",
        side_effect=[False, True],
    ):
        result = check_task(task)

    assert result.structurally_valid
    assert not result.passed

    assert result.environment.attempted
    assert result.environment.succeeded is False

    assert result.tests.attempted
    assert result.tests.succeeded is True


def test_image_tag_is_stable_for_repository_task():
    task = Path(__file__).resolve().parents[1] / "cuda-gpu" / "cuda-shared-memory-001"

    tag = image_tag(task, "tests")

    assert tag == "benchmark-smoke-cuda-gpu-cuda-shared-memory-001-tests"


def test_image_tag_is_stable_for_external_task(tmp_path: Path):
    task = tmp_path / "category" / "sample-task"
    task.mkdir(parents=True)

    first = image_tag(task, "environment")
    second = image_tag(task, "environment")

    assert first == second
    assert first.startswith("benchmark-smoke-sample-task-")
    assert first.endswith("-environment")
