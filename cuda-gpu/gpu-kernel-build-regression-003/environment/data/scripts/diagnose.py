#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"


CONFIG_SOURCES = [
    "build.conf",
    "release.profile",
    "benchmark.conf",
    "local.override",
]


def parse_key_values(path: Path) -> dict[str, str]:
    values = {}

    if not path.exists():
        return values

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()

    return values


def collect_provenance() -> dict[str, list[tuple[str, str]]]:
    provenance = {}

    for filename in CONFIG_SOURCES:
        values = parse_key_values(CONFIG_DIR / filename)

        for key, value in values.items():
            provenance.setdefault(key, []).append((filename, value))

    return provenance


def print_sources() -> None:
    print("\n[Configuration sources]")

    for filename in CONFIG_SOURCES:
        path = CONFIG_DIR / filename

        if path.exists():
            print(f"- {filename}: present")
        else:
            print(f"- {filename}: missing")


def print_provenance() -> None:
    provenance = collect_provenance()

    print("\n[Configuration provenance]")

    for key in sorted(provenance):
        entries = provenance[key]

        rendered = " -> ".join(f"{source}:{value}" for source, value in entries)

        print(f"{key}: {rendered}")


def print_effective_config() -> None:
    path = BUILD_DIR / "effective_config.txt"

    print("\n[Effective configuration]")

    if not path.exists():
        print("Effective configuration: missing")
        return

    values = parse_key_values(path)

    for key in sorted(values):
        print(f"{key}={values[key]}")


def print_artifact() -> None:
    path = ARTIFACT_DIR / "kernel_build.artifact"

    print("\n[Generated artifact]")

    if not path.exists():
        print("Artifact: missing")
        return

    values = parse_key_values(path)

    for key in (
        "BUILD_TYPE",
        "OPT_LEVEL",
        "FAST_MATH",
        "VECTOR_WIDTH",
        "DEBUG_SYMBOLS",
        "LTO",
        "ARTIFACT_MODE",
    ):
        if key in values:
            print(f"{key}={values[key]}")


def print_contract() -> None:
    contract_path = ROOT / "reference" / "optimization_contract.txt"

    print("\n[Expected contract]")

    if not contract_path.exists():
        print("Reference contract is not available.")
        return

    values = parse_key_values(contract_path)

    for key in (
        "BUILD_TYPE",
        "OPT_LEVEL",
        "FAST_MATH",
        "VECTOR_WIDTH",
        "DEBUG_SYMBOLS",
        "LTO",
        "ARTIFACT_MODE",
        "BENCHMARK_SCORE_MIN",
    ):
        if key in values:
            print(f"{key}={values[key]}")


def main() -> int:
    print("=== GPU BUILD DIAGNOSTIC ===")

    print_sources()
    print_provenance()
    print_effective_config()
    print_artifact()
    print_contract()

    print("\n[Diagnostic status]")

    effective = BUILD_DIR / "effective_config.txt"
    artifact = ARTIFACT_DIR / "kernel_build.artifact"

    if not effective.exists():
        print("STATUS=NOT_BUILT")
    elif not artifact.exists():
        print("STATUS=ARTIFACT_MISSING")
    else:
        print("STATUS=INSPECTION_REQUIRED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
