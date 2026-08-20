from pathlib import Path


def test_ci_contains_checkov_iac_scan():
    workflow = Path(".github/workflows/ci.yml").read_text()

    assert "checkov" in workflow.lower()
    assert "dockerfile" in workflow.lower()
    assert "kubernetes" in workflow.lower()
