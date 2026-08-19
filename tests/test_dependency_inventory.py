from pathlib import Path

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
