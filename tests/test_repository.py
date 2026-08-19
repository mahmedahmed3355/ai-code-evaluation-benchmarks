from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def task_dirs():
    for task_file in ROOT.rglob("task.toml"):
        if ".git" not in task_file.parts:
            yield task_file.parent


def test_repository_contains_tasks():
    tasks = list(task_dirs())
    assert len(tasks) >= 17


def test_every_task_has_instruction():
    missing = []

    for task in task_dirs():
        if not ((task / "instruction.md").exists() or (task / "instruction_en.md").exists()):
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


def test_requirements_lock_exists_and_is_not_empty():
    lockfile = ROOT / "requirements.lock"

    assert lockfile.exists(), "requirements.lock is missing"
    assert lockfile.stat().st_size > 0, "requirements.lock is empty"


def test_root_dockerfile_exists():
    dockerfile = ROOT / "Dockerfile"

    assert dockerfile.exists(), "Root Dockerfile is missing"


def test_docker_compose_exists():
    compose = ROOT / "docker-compose.yml"

    assert compose.exists(), "docker-compose.yml is missing"


def test_requirements_lock_is_fully_pinned():
    lockfile = ROOT / "requirements.lock"

    assert lockfile.exists()

    package_lines = []

    for raw_line in lockfile.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or line.startswith("--") or line.startswith("\\"):
            continue

        package_lines.append(line)

    assert package_lines

    for line in package_lines:
        if "@" in line:
            continue

        assert "==" in line, f"Dependency is not exactly pinned: {line}"


def test_task_validation_reports_missing_structure(tmp_path, monkeypatch):
    from scripts import validate_tasks

    broken_task = tmp_path / "broken-task"
    broken_task.mkdir()
    (broken_task / "task.toml").write_text('name = "broken-task"')

    monkeypatch.setattr(validate_tasks, "ROOT", tmp_path)

    tasks = list(validate_tasks.task_dirs())

    assert tasks == [broken_task]


def test_requirements_input_exists():
    requirements_in = ROOT / "requirements.in"

    assert requirements_in.exists()
    assert requirements_in.read_text(encoding="utf-8").strip()


def test_validation_metrics_module_exists():
    metrics_module = ROOT / "scripts" / "validation_metrics.py"

    assert metrics_module.exists()
    assert metrics_module.read_text(encoding="utf-8").strip()


def test_validator_uses_validation_metrics():
    validator = ROOT / "scripts" / "validate_tasks.py"

    content = validator.read_text(encoding="utf-8")

    assert "ValidationMetrics" in content
    assert "record_success()" in content
    assert "record_failure()" in content
