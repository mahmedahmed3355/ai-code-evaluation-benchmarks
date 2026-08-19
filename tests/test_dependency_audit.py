from pathlib import Path

from scripts.check_task_dependencies import check_file


def test_dependency_audit_accepts_requirements_manifest(tmp_path: Path):
    dockerfile = tmp_path / "Dockerfile"

    dockerfile.write_text(
        """
        FROM python:3.12
        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt
        """
    )

    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "numpy==2.3.2\n"
    )

    result = check_file(dockerfile)

    assert result == []
