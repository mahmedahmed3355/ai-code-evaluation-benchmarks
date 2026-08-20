from pathlib import Path

from scripts.validate_k8s_security import (
    validate_document,
)

SOURCE = Path("deployment.yaml")


def valid_deployment() -> dict:
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "example"},
        "spec": {
            "template": {
                "spec": {
                    "securityContext": {
                        "runAsNonRoot": True,
                    },
                    "containers": [
                        {
                            "name": "app",
                            "securityContext": {
                                "allowPrivilegeEscalation": False,
                                "privileged": False,
                                "capabilities": {
                                    "drop": ["NET_RAW"],
                                },
                            },
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "128Mi",
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "512Mi",
                                },
                            },
                        }
                    ],
                }
            }
        },
    }


def test_valid_workload_passes() -> None:
    assert validate_document(valid_deployment(), SOURCE) == []


def test_missing_run_as_non_root_is_flagged() -> None:
    document = valid_deployment()
    document["spec"]["template"]["spec"]["securityContext"] = {}

    errors = validate_document(document, SOURCE)

    assert any("runAsNonRoot=true" in error for error in errors)


def test_host_network_is_flagged() -> None:
    document = valid_deployment()
    document["spec"]["template"]["spec"]["hostNetwork"] = True

    errors = validate_document(document, SOURCE)

    assert any("hostNetwork=true" in error for error in errors)


def test_host_pid_is_flagged() -> None:
    document = valid_deployment()
    document["spec"]["template"]["spec"]["hostPID"] = True

    errors = validate_document(document, SOURCE)

    assert any("hostPID=true" in error for error in errors)


def test_privileged_container_is_flagged() -> None:
    document = valid_deployment()

    document["spec"]["template"]["spec"]["containers"][0][
        "securityContext"
    ]["privileged"] = True

    errors = validate_document(document, SOURCE)

    assert any("must not be privileged" in error for error in errors)


def test_privilege_escalation_must_be_disabled() -> None:
    document = valid_deployment()

    document["spec"]["template"]["spec"]["containers"][0][
        "securityContext"
    ] = {}

    errors = validate_document(document, SOURCE)

    assert any(
        "allowPrivilegeEscalation=false" in error
        for error in errors
    )


def test_non_workload_resource_is_ignored() -> None:
    document = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": "example"},
        "data": {"key": "value"},
    }

    assert validate_document(document, SOURCE) == []


def test_kustomize_base_includes_network_policy() -> None:
    kustomization = Path(
        "infrastructure/kubernetes-rollout-recovery-010/base/kustomization.yaml"
    )

    text = kustomization.read_text()

    assert "deployment.yaml" in text
    assert "network-policy.yaml" in text
