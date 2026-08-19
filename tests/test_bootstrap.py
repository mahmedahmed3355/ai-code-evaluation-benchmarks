from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_makefile_exposes_setup_target():
    content = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "setup:" in content
    assert "uv sync --extra dev --locked" in content


def test_makefile_exposes_smoke_target():
    content = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "smoke:" in content
    assert "$(MAKE) validate-all" in content


def test_makefile_exposes_task_smoke_target():
    content = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "task-smoke:" in content
    assert "uv run python -m scripts.task_isolation" in content


def test_makefile_exposes_task_manifest_target():
    content = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "task-manifest:" in content
    assert "uv run python -m scripts.task_manifest" in content


def test_uv_lock_exists_for_reproducible_bootstrap():
    lockfile = ROOT / "uv.lock"

    assert lockfile.is_file()
    assert lockfile.stat().st_size > 0
