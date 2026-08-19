#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")

CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"
REPORT_DIR = ROOT / "reports"
LOG_DIR = ROOT / "logs"

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


def print_configuration_sources() -> None:
    print("\n[Configuration sources]")

    for name in CONFIG_SOURCES:
        path = CONFIG_DIR / name

        if path.exists():
            print(f"- {name}: present")
        else:
            print(f"- {name}: missing")


def print_provenance() -> None:
    print("\n[Configuration provenance]")

    provenance = {}

    for name in CONFIG_SOURCES:
        values = parse_key_values(CONFIG_DIR / name)

        for key, value in values.items():
            provenance.setdefault(key, []).append((name, value))

    for key in sorted(provenance):
        entries = provenance[key]

        rendered = " -> ".join(f"{source}:{value}" for source, value in entries)

        print(f"{key}: {rendered}")


def print_effective_configuration() -> None:
    print("\n[Effective configuration]")

    path = BUILD_DIR / "resolved_config.txt"

    if not path.exists():
        print("Resolved configuration: missing")
        return

    values = parse_key_values(path)

    for key in sorted(values):
        print(f"{key}={values[key]}")


def print_execution_plan() -> None:
    print("\n[Execution plan]")

    path = BUILD_DIR / "execution_plan.txt"

    if not path.exists():
        print("Execution plan: missing")
        return

    values = parse_key_values(path)

    for key in sorted(values):
        print(f"{key}={values[key]}")


def print_artifact() -> None:
    print("\n[Generated artifact]")

    path = ARTIFACT_DIR / "kernel_build.artifact"

    if not path.exists():
        print("Artifact: missing")
        return

    values = parse_key_values(path)

    for key in sorted(values):
        print(f"{key}={values[key]}")


def print_benchmark_report() -> None:
    print("\n[Benchmark report]")

    path = REPORT_DIR / "benchmark.txt"

    if not path.exists():
        print("Benchmark report: missing")
        return

    values = parse_key_values(path)

    for key in sorted(values):
        print(f"{key}={values[key]}")


def print_history() -> None:
    print("\n[Build history]")

    path = LOG_DIR / "build-history.log"

    if not path.exists():
        print("Build history: missing")
        return

    print(path.read_text())


def print_diagnostic_status() -> None:
    print("\n[Diagnostic status]")

    resolved = BUILD_DIR / "resolved_config.txt"
    plan = BUILD_DIR / "execution_plan.txt"
    artifact = ARTIFACT_DIR / "kernel_build.artifact"
    report = REPORT_DIR / "benchmark.txt"

    if not resolved.exists():
        print("STATUS=NOT_BUILT")
    elif not plan.exists():
        print("STATUS=PLAN_MISSING")
    elif not artifact.exists():
        print("STATUS=ARTIFACT_MISSING")
    elif not report.exists():
        print("STATUS=BENCHMARK_NOT_RUN")
    else:
        print("STATUS=INSPECTION_COMPLETE")


def main() -> int:
    print("=== GPU KERNEL PERFORMANCE DIAGNOSTIC ===")

    print_configuration_sources()
    print_provenance()
    print_effective_configuration()
    print_execution_plan()
    print_artifact()
    print_benchmark_report()
    print_history()
    print_diagnostic_status()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
