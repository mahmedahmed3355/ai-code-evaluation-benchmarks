from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
K8S_ROOT = ROOT / "infrastructure" / "kubernetes-rollout-recovery-010"

WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"}


def workload_spec(document: dict[str, Any]) -> dict[str, Any] | None:
    kind = document.get("kind")

    if kind not in WORKLOAD_KINDS:
        return None

    spec = document.get("spec", {})

    if kind == "CronJob":
        return (
            spec.get("jobTemplate", {})
            .get("spec", {})
            .get("template", {})
            .get("spec")
        )

    return spec.get("template", {}).get("spec")


def validate_document(
    document: dict[str, Any],
    source: Path,
) -> list[str]:
    pod_spec = workload_spec(document)

    if pod_spec is None:
        return []

    errors: list[str] = []

    security_context = pod_spec.get("securityContext", {})

    if security_context.get("runAsNonRoot") is not True:
        errors.append(
            f"{source}: workload must set securityContext.runAsNonRoot=true"
        )

    if pod_spec.get("hostNetwork") is True:
        errors.append(f"{source}: hostNetwork=true is not allowed")

    if pod_spec.get("hostPID") is True:
        errors.append(f"{source}: hostPID=true is not allowed")

    containers = pod_spec.get("containers", [])

    for container in containers:
        name = container.get("name", "<unnamed>")
        container_security = container.get("securityContext", {})

        if container_security.get("privileged") is True:
            errors.append(
                f"{source}: container {name} must not be privileged"
            )

        if (
            container_security.get("allowPrivilegeEscalation")
            is not False
        ):
            errors.append(
                f"{source}: container {name} must set "
                "allowPrivilegeEscalation=false"
            )

    return errors


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []

    for document in yaml.safe_load_all(
        path.read_text(encoding="utf-8")
    ):
        if not isinstance(document, dict):
            continue

        errors.extend(validate_document(document, path))

    return errors


def manifest_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".yaml", ".yml"}
        and path.name != "kustomization.yaml"
    )


def main() -> int:
    files = manifest_files(K8S_ROOT)

    if not files:
        print(f"No Kubernetes manifests found under {K8S_ROOT}")
        return 1

    errors: list[str] = []

    for path in files:
        errors.extend(validate_file(path))

    if errors:
        print("Kubernetes security policy validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        "Kubernetes security policy validation passed "
        f"for {len(files)} manifest(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
