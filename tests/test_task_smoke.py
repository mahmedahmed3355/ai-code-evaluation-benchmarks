from pathlib import Path

from scripts.task_smoke import smoke_task


def test_task_smoke_validates_task_structure(tmp_path: Path):
    task = tmp_path

    for file in [
        "environment/Dockerfile",
        "tests/Dockerfile",
        "solution/solve.sh",
        "tests/test.sh",
    ]:
        path = task / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")

    assert smoke_task(task)
