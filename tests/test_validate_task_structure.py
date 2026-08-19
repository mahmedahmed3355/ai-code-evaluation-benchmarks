from pathlib import Path

from scripts.validate_task_structure import (
    task_directories,
    validate_task,
)


def create_valid_task(root: Path) -> Path:
    task = root / "sample-task"

    (task / "environment").mkdir(parents=True)
    (task / "solution").mkdir()
    (task / "tests").mkdir()

    (task / "task.toml").write_text(
        "[task]\nname = 'sample'\n",
        encoding="utf-8",
    )

    (task / "instruction.md").write_text(
        "# Sample task\n",
        encoding="utf-8",
    )

    (task / "environment" / "Dockerfile").write_text(
        "FROM scratch\n",
        encoding="utf-8",
    )

    (task / "solution" / "solve.sh").write_text(
        "#!/bin/sh\nexit 0\n",
        encoding="utf-8",
    )

    (task / "tests" / "Dockerfile").write_text(
        "FROM scratch\n",
        encoding="utf-8",
    )

    (task / "tests" / "test.sh").write_text(
        "#!/bin/sh\nexit 0\n",
        encoding="utf-8",
    )

    return task


def test_valid_task_passes(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    assert validate_task(task) == []


def test_instruction_en_is_accepted(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    (task / "instruction.md").unlink()
    (task / "instruction_en.md").write_text(
        "# English task\n",
        encoding="utf-8",
    )

    assert validate_task(task) == []


def test_missing_task_file_is_flagged(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    (task / "task.toml").unlink()

    assert "missing required path: task.toml" in validate_task(task)


def test_missing_instruction_is_flagged(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    (task / "instruction.md").unlink()

    errors = validate_task(task)

    assert (
        "missing instruction file: instruction.md or instruction_en.md"
        in errors
    )


def test_missing_environment_dockerfile_is_flagged(
    tmp_path: Path,
) -> None:
    task = create_valid_task(tmp_path)

    (task / "environment" / "Dockerfile").unlink()

    errors = validate_task(task)

    assert (
        "environment must contain Dockerfile or docker-compose file"
        in errors
    )


def test_empty_solution_is_flagged(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    (task / "solution" / "solve.sh").write_text(
        "",
        encoding="utf-8",
    )

    assert "solution/solve.sh must not be empty" in validate_task(task)


def test_empty_test_script_is_flagged(tmp_path: Path) -> None:
    task = create_valid_task(tmp_path)

    (task / "tests" / "test.sh").write_text(
        "",
        encoding="utf-8",
    )

    assert "tests/test.sh must not be empty" in validate_task(task)


def test_task_directories_discovers_tasks(tmp_path: Path) -> None:
    first = tmp_path / "one"
    second = tmp_path / "nested" / "two"

    first.mkdir(parents=True)
    second.mkdir(parents=True)

    (first / "task.toml").write_text("", encoding="utf-8")
    (second / "task.toml").write_text("", encoding="utf-8")

    discovered = task_directories(tmp_path)

    assert discovered == [first, second]
