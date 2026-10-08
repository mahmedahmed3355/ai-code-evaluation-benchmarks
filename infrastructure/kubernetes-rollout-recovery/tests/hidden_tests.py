from pathlib import Path
import os, yaml, tempfile, shutil, subprocess
D=Path(os.environ.get("TASK_DATA", "/app/data"))
def test_all_selectors_have_same_keys_and_values():
    d=yaml.safe_load((D/"deployment.yaml").read_text())
    s=yaml.safe_load((D/"service.yaml").read_text())
    p=yaml.safe_load((D/"pdb.yaml").read_text())
    want=d["spec"]["template"]["metadata"]["labels"]
    assert d["spec"]["selector"]["matchLabels"]==want
    assert s["spec"]["selector"]==want
    assert p["spec"]["selector"]["matchLabels"]==want

def test_release_label_is_not_mixed():
    for n in ("deployment.yaml","service.yaml","pdb.yaml"):
        x=yaml.safe_load((D/n).read_text())
        text=(D/n).read_text()
        assert "2025-12" not in text
        assert "2026-10" in text
