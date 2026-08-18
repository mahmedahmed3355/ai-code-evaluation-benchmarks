from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def task_dirs():
    for task_file in ROOT.rglob("task.toml"):
        if ".git" not in task_file.parts:
            yield task_file.parent


def test_repository_contains_tasks():
    tasks = list(task_dirs())
    assert len(tasks) >= 20


def test_every_task_has_instruction():
    missing = []

    for task in task_dirs():
        if not (
            (task / "instruction.md").exists()
            or (task / "instruction_en.md").exists()
        ):
            missing.append(str(task.relative_to(ROOT)))

    assert not missing, f"Tasks missing instructions: {missing}"


def test_every_task_has_solution():
    missing = []

    for task in task_dirs():
        if not (task / "solution" / "solve.sh").exists():
            missing.append(str(task.relative_to(ROOT)))

    assert not missing, f"Tasks missing solutions: {missing}"


def test_every_task_has_tests():
    missing = []

    for task in task_dirs():
        tests_dir = task / "tests"

        if not tests_dir.exists():
            missing.append(str(task.relative_to(ROOT)))

    assert not missing, f"Tasks missing tests directory: {missing}"


def test_task_toml_has_name():
    missing = []

    for task in task_dirs():
        content = (task / "task.toml").read_text(
            encoding="utf-8",
            errors="ignore",
        )

        if "name =" not in content:
            missing.append(str(task.relative_to(ROOT)))

    assert not missing, f"Tasks missing name metadata: {missing}"
