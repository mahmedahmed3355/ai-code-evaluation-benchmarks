from scripts.task_smoke import smoke_task


def test_real_task_smoke():
    from pathlib import Path

    task = Path("cuda-gpu/cuda-shared-memory-001")

    assert task.exists()
    assert smoke_task(task)
