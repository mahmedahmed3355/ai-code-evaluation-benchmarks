from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_uv_lock_exists():
    lockfile = ROOT / "uv.lock"

    assert lockfile.is_file()
    assert lockfile.stat().st_size > 0


def test_makefile_uses_locked_uv_install():
    makefile = ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")

    assert "uv sync --group dev --locked" in content
    assert "validate-all:" in content
    assert "lock-check:" in content


def test_makefile_exposes_repository_quality_targets():
    makefile = ROOT / "Makefile"
    content = makefile.read_text(encoding="utf-8")

    for target in (
        "test:",
        "lint:",
        "typecheck:",
        "validate:",
        "coverage:",
        "audit:",
    ):
        assert target in content
