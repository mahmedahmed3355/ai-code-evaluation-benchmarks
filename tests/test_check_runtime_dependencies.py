from pathlib import Path

import pytest

import scripts.check_runtime_dependencies as runtime_dependencies


def test_get_runtime_dependencies_reads_project_dependencies(
    tmp_path: Path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = [
    "pyyaml==6.0.2",
    "httpx==0.28.1",
]
""".strip()
    )

    monkeypatch.setattr(runtime_dependencies, "PYPROJECT", pyproject)

    assert runtime_dependencies.get_runtime_dependencies() == [
        "pyyaml==6.0.2",
        "httpx==0.28.1",
    ]


def test_validate_runtime_dependencies_returns_declared_dependencies(
    tmp_path: Path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = ["pyyaml==6.0.2"]
""".strip()
    )

    monkeypatch.setattr(runtime_dependencies, "PYPROJECT", pyproject)

    assert runtime_dependencies.validate_runtime_dependencies() == [
        "pyyaml==6.0.2",
    ]


def test_validate_runtime_dependencies_rejects_empty_dependency_set(
    tmp_path: Path,
    monkeypatch,
):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = []
""".strip()
    )

    monkeypatch.setattr(runtime_dependencies, "PYPROJECT", pyproject)

    with pytest.raises(ValueError, match="runtime dependency set is empty"):
        runtime_dependencies.validate_runtime_dependencies()


def test_main_returns_success_when_dependencies_exist(
    monkeypatch,
):
    monkeypatch.setattr(
        runtime_dependencies,
        "validate_runtime_dependencies",
        lambda: ["pyyaml==6.0.2"],
    )

    assert runtime_dependencies.main() == 0
