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
