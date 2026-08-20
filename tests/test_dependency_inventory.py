from pathlib import Path

import scripts.generate_dependency_inventory as dependency_inventory
from scripts.generate_dependency_inventory import find_requirements


def test_find_requirements(tmp_path: Path):
    task = tmp_path / "task"

    env = task / "environment"
    env.mkdir(parents=True)

    (env / "requirements.txt").write_text(
        "numpy==2.3.2\nscipy==1.15.0\n"
    )

    result = find_requirements(task)

    assert result == [
        "numpy==2.3.2",
        "scipy==1.15.0",
    ]


def test_find_requirements_ignores_comments_blank_lines_and_duplicates(
    tmp_path: Path,
):
    task = tmp_path / "task"
    first = task / "environment"
    second = task / "nested"

    first.mkdir(parents=True)
    second.mkdir(parents=True)

    (first / "requirements.txt").write_text(
        "# runtime dependencies\n"
        "\n"
        "numpy==2.3.2\n"
        "scipy==1.15.0\n"
    )

    (second / "requirements.txt").write_text(
        "numpy==2.3.2\n"
        "\n"
        "# duplicate\n"
    )

    assert find_requirements(task) == [
        "numpy==2.3.2",
        "scipy==1.15.0",
    ]


def test_find_repository_dependencies_reads_runtime_and_dev(
    tmp_path: Path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = [
    "pyyaml==6.0.2",
    "pydantic==2.11.0",
]

[dependency-groups]
dev = [
    "pytest==9.0.3",
    "ruff==0.12.11",
]
""".strip()
    )

    monkeypatch.setattr(dependency_inventory, "ROOT", tmp_path)

    runtime, dev = dependency_inventory.find_repository_dependencies()

    assert runtime == [
        "pydantic==2.11.0",
        "pyyaml==6.0.2",
    ]
    assert dev == [
        "pytest==9.0.3",
        "ruff==0.12.11",
    ]


def test_find_repository_dependencies_returns_empty_when_missing(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setattr(dependency_inventory, "ROOT", tmp_path)

    runtime, dev = dependency_inventory.find_repository_dependencies()

    assert runtime == []
    assert dev == []


def test_generate_writes_repository_and_task_dependencies(
    tmp_path: Path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = ["pyyaml==6.0.2"]

[dependency-groups]
dev = ["pytest==9.0.3"]
""".strip()
    )

    task = tmp_path / "cuda-gpu" / "example-task"
    task.mkdir(parents=True)

    (task / "task.toml").write_text("[task]\nname = \"example\"\n")

    environment = task / "environment"
    environment.mkdir()

    (environment / "requirements.txt").write_text(
        "numpy==2.3.2\n"
    )

    output = tmp_path / "docs" / "TASK_DEPENDENCIES.md"

    monkeypatch.setattr(dependency_inventory, "ROOT", tmp_path)
    monkeypatch.setattr(dependency_inventory, "OUTPUT", output)

    result = dependency_inventory.generate()

    assert result == output
    assert output.exists()

    content = output.read_text()

    assert "## Repository Runtime Dependencies" in content
    assert "- `pyyaml==6.0.2`" in content

    assert "## Repository Development Dependencies" in content
    assert "- `pytest==9.0.3`" in content

    assert "## cuda-gpu/example-task" in content
    assert "- `numpy==2.3.2`" in content


def test_generate_reports_when_no_task_dependencies(
    tmp_path: Path,
    monkeypatch,
):
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
dependencies = []

[dependency-groups]
dev = []
""".strip()
    )

    task = tmp_path / "task"
    task.mkdir()

    (task / "task.toml").write_text("[task]\nname = \"empty\"\n")

    output = tmp_path / "docs" / "TASK_DEPENDENCIES.md"

    monkeypatch.setattr(dependency_inventory, "ROOT", tmp_path)
    monkeypatch.setattr(dependency_inventory, "OUTPUT", output)

    dependency_inventory.generate()

    content = output.read_text()

    assert "No task-local requirements manifests found." in content


def test_main_calls_generate(monkeypatch):
    called = []

    def fake_generate():
        called.append(True)
        return Path("unused")

    monkeypatch.setattr(
        dependency_inventory,
        "generate",
        fake_generate,
    )

    assert dependency_inventory.main() == 0
    assert called == [True]
