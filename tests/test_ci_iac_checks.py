from pathlib import Path


def test_ci_contains_checkov_iac_scan():
    workflow = Path(".github/workflows/ci.yml").read_text()

    assert "checkov" in workflow.lower()
    assert "dockerfile" in workflow.lower()
    assert "kubernetes" in workflow.lower()


def test_ci_contains_terraform_validation():
    workflow = Path(".github/workflows/ci.yml").read_text()

    assert "terraform-checks:" in workflow
    assert "terraform fmt -check -recursive infra" in workflow
    assert "terraform init -backend=false" in workflow
    assert "terraform validate" in workflow
    assert "terraform plan -refresh=false -input=false" in workflow
    assert "framework: terraform" in workflow


def test_benchmark_namespace_module_exists():
    module = Path("infra/modules/benchmark-namespace")

    assert (module / "main.tf").exists()
    assert (module / "variables.tf").exists()
    assert (module / "outputs.tf").exists()
    assert (module / "versions.tf").exists()


def test_terraform_module_uses_pinned_provider():
    versions = Path(
        "infra/modules/benchmark-namespace/versions.tf"
    ).read_text()

    assert 'source  = "hashicorp/kubernetes"' in versions
    assert 'version = "~> 2.36"' in versions


def test_terraform_module_creates_isolated_namespace():
    main = Path(
        "infra/modules/benchmark-namespace/main.tf"
    ).read_text()

    assert 'resource "kubernetes_namespace_v1" "benchmark"' in main
    assert '"benchmark.ai/isolation"       = "enabled"' in main
    assert '"pod-security.kubernetes.io/enforce"         = "restricted"' in main
