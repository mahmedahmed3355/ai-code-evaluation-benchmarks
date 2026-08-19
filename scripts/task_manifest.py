from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = (
    "metadata",
    "verifier",
    "agent",
    "environment",
)


@dataclass(frozen=True)
class ManifestValidationResult:
    path: Path
    errors: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def _is_positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value > 0
    )


def _is_non_negative_integer(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _load_manifest(path: Path) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    try:
        with path.open("rb") as manifest_file:
            data = tomllib.load(manifest_file)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return None, (f"invalid TOML: {exc}",)

    return data, ()


def validate_manifest(path: Path) -> ManifestValidationResult:
    data, load_errors = _load_manifest(path)

    if load_errors:
        return ManifestValidationResult(path=path, errors=load_errors)

    assert data is not None
    errors: list[str] = []

    for section in REQUIRED_SECTIONS:
        value = data.get(section)
        if not isinstance(value, dict):
            errors.append(f"missing or invalid [{section}] section")

    task = data.get("task")
    if task is not None:
        if not isinstance(task, dict):
            errors.append("invalid [task] section")
        elif not isinstance(task.get("name"), str) or not task["name"].strip():
            errors.append("missing or invalid task.name")

    verifier = data.get("verifier")
    if isinstance(verifier, dict):
        timeout = verifier.get("timeout_sec")
        if not _is_positive_number(timeout):
            errors.append("verifier.timeout_sec must be positive")

    agent = data.get("agent")
    if isinstance(agent, dict):
        timeout = agent.get("timeout_sec")
        if not _is_positive_number(timeout):
            errors.append("agent.timeout_sec must be positive")

    environment = data.get("environment")
    if isinstance(environment, dict):
        build_timeout = environment.get("build_timeout_sec")
        if not _is_positive_number(build_timeout):
            errors.append("environment.build_timeout_sec must be positive")

        for field in ("cpus", "memory_mb", "storage_mb"):
            value = environment.get(field)
            if not _is_positive_number(value):
                errors.append(f"environment.{field} must be positive")

        gpus = environment.get("gpus")
        if not _is_non_negative_integer(gpus):
            errors.append("environment.gpus must be a non-negative integer")

        if "allow_internet" in environment and not isinstance(
            environment["allow_internet"], bool
        ):
            errors.append("environment.allow_internet must be a boolean")

    return ManifestValidationResult(path=path, errors=tuple(errors))
