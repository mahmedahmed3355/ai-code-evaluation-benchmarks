from pathlib import Path

import scripts.check_task_deps as task_deps
from scripts.check_task_deps import (
    docker_instructions,
    is_pinned_image,
    pip_install_has_unpinned_package,
)


def test_pinned_image_with_tag() -> None:
    assert is_pinned_image("python:3.13-slim-bookworm")


def test_digest_pinned_image() -> None:
    assert is_pinned_image(
        "python@sha256:"
        "0123456789abcdef0123456789abcdef"
        "0123456789abcdef0123456789abcdef"
    )


def test_unpinned_image() -> None:
    assert not is_pinned_image("python")


def test_scratch_image_is_allowed() -> None:
    assert is_pinned_image("scratch")


def test_requirement_file_is_not_flagged() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install --no-cache-dir -r requirements.txt"
    )


def test_pinned_package_is_not_flagged() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install --no-cache-dir pytest==9.0.3"
    )


def test_unpinned_package_is_flagged() -> None:
    assert pip_install_has_unpinned_package(
        "RUN pip install --no-cache-dir pytest"
    )


def test_docker_instructions_handles_continuations() -> None:
    text = """\
FROM python:3.13-slim-bookworm
RUN apt-get update && \\
    apt-get install -y curl
RUN pip install --no-cache-dir pytest==9.0.3
"""

    instructions = docker_instructions(text)

    assert len(instructions) == 3
    assert instructions[0] == "FROM python:3.13-slim-bookworm"
    assert "apt-get install -y curl" in instructions[1]
    assert "pytest==9.0.3" in instructions[2]


def test_multiline_pinned_packages_are_not_flagged() -> None:
    command = """\
RUN pip install --no-cache-dir \\
    pytest==8.4.1 \\
    fastapi==0.116.1 \\
    httpx==0.28.1 \\
    uvicorn==0.35.0
"""

    assert not pip_install_has_unpinned_package(command)


def test_multiline_unpinned_package_is_flagged() -> None:
    command = """\
RUN pip install --no-cache-dir \\
    pytest==8.4.1 \\
    fastapi \\
    httpx==0.28.1
"""

    assert pip_install_has_unpinned_package(command)
def test_pinned_image_with_registry_port() -> None:
    assert is_pinned_image("registry.example.com:5000/app:1.0.0")


def test_pip_install_git_dependency_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install package@git+https://example.com/repo.git"
    )


def test_pip_install_http_dependency_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install package@https://example.com/package.whl"
    )


def test_pip_install_constraint_file_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install -c constraints.txt"
    )


def test_pip_install_local_project_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install ."
    )


def test_non_pip_command_is_not_flagged() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN echo hello"
    )

def test_pip_install_requirement_long_option_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install --requirement requirements.txt"
    )


def test_pip_install_constraint_long_option_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install --constraint constraints.txt"
    )


def test_pip_install_stops_at_shell_separator() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install pytest==9.0.3 && echo done"
    )


def test_unpinned_package_before_shell_separator_is_flagged() -> None:
    assert pip_install_has_unpinned_package(
        "RUN pip install pytest && echo done"
    )


def test_pip_install_with_editable_flag_and_pinned_package_is_allowed() -> None:
    assert not pip_install_has_unpinned_package(
        "RUN pip install -e pytest==9.0.3"
    )


def test_docker_instructions_handles_empty_input() -> None:
    assert docker_instructions("") == []


def test_docker_instructions_handles_unterminated_instruction() -> None:
    instructions = docker_instructions(
        "RUN pip install pytest==9.0.3 \\\n"
    )

    assert instructions == [
        "RUN pip install pytest==9.0.3 \\"
    ]




def test_main_returns_zero_when_all_dependencies_are_pinned(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        "FROM python:3.13-slim-bookworm\n"
        "RUN pip install pytest==9.0.3\n"
    )

    monkeypatch.setattr(task_deps, "ROOT", tmp_path)

    assert task_deps.main() == 0


def test_main_returns_one_for_unpinned_base_image(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        "FROM python\n"
        "RUN pip install pytest==9.0.3\n"
    )

    monkeypatch.setattr(task_deps, "ROOT", tmp_path)

    assert task_deps.main() == 1


def test_main_returns_one_for_unpinned_pip_dependency(
    tmp_path: Path,
    monkeypatch,
) -> None:
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        "FROM python:3.13-slim-bookworm\n"
        "RUN pip install pytest\n"
    )

    monkeypatch.setattr(task_deps, "ROOT", tmp_path)

    assert task_deps.main() == 1
