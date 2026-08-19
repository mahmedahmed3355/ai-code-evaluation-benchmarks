from pathlib import Path

import scripts.validate_tasks as validator


def create_task(root: Path, category: str, name: str) -> Path:
    task_dir = root / category / name
    task_dir.mkdir(parents=True)

    for required in validator.REQUIRED_FILES:
        path = task_dir / required
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("test\n", encoding="utf-8")

    (task_dir / "task.toml").write_text(
        'name = "sample-task"\n',
        encoding="utf-8",
    )

    return task_dir


def test_task_dirs_finds_task_directories(tmp_path: Path, monkeypatch):
    create_task(tmp_path, "category-a", "task-one")
    create_task(tmp_path, "category-b", "task-two")

    monkeypatch.setattr(validator, "ROOT", tmp_path)

    task_paths = list(validator.task_dirs())

    assert len(task_paths) == 2
    assert tmp_path / "category-a" / "task-one" in task_paths
    assert tmp_path / "category-b" / "task-two" in task_paths


def test_main_returns_error_when_no_tasks_found(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(validator, "ROOT", tmp_path)

    result = validator.main()

    captured = capsys.readouterr()

    assert result == 1
    assert "ERROR: No tasks found." in captured.out


def test_main_passes_when_task_is_complete(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    create_task(tmp_path, "category", "complete-task")

    monkeypatch.setattr(validator, "ROOT", tmp_path)

    result = validator.main()

    captured = capsys.readouterr()

    assert result == 0
    assert "Found 1 tasks" in captured.out
    assert "PASS: category/complete-task" in captured.out
    assert "total=1" in captured.out
    assert "passed=1" in captured.out
    assert "failed=0" in captured.out
    assert "success_rate=100.00%" in captured.out
    assert "SUCCESS: All 1 tasks have the required structure." in captured.out


def test_main_reports_missing_files(
    tmp_path: Path,
    monkeypatch,
    capsys,
):
    task_dir = create_task(tmp_path, "category", "broken-task")

    (task_dir / "instruction.md").unlink()
    (task_dir / "solution" / "solve.sh").unlink()

    monkeypatch.setattr(validator, "ROOT", tmp_path)

    result = validator.main()

    captured = capsys.readouterr()

    assert result == 1
    assert "FAIL: category/broken-task" in captured.out
    assert "missing: instruction.md" in captured.out
    assert "missing: solution/solve.sh" in captured.out
    assert "total=1" in captured.out
    assert "passed=0" in captured.out
    assert "failed=1" in captured.out
    assert "success_rate=0.00%" in captured.out
    assert "Validation failed: 1 task(s) have missing files." in captured.out
