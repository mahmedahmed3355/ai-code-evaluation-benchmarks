#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"
REPORT_DIR = ROOT / "reports"
LOG_DIR = ROOT / "logs"

SOURCES = ["build.conf", "release.profile", "benchmark.conf", "local.override"]

def parse(path):
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values

def show(title, values):
    print(f"\n[{title}]")
    for key in sorted(values):
        print(f"{key}={values[key]}")

def main():
    print("=== GPU KERNEL PERFORMANCE DIAGNOSTIC ===")
    print("\n[Configuration sources]")
    for name in SOURCES:
        print(f"{name}={'present' if (CONFIG_DIR / name).exists() else 'missing'}")
    print("\n[Configuration provenance]")
    provenance = {}
    for name in SOURCES:
        for key, value in parse(CONFIG_DIR / name).items():
            provenance.setdefault(key, []).append(f"{name}:{value}")
    for key in sorted(provenance):
        print(f"{key}: {' -> '.join(provenance[key])}")
    show("Effective configuration", parse(BUILD_DIR / "resolved_config.txt"))
    show("Execution plan", parse(BUILD_DIR / "execution_plan.txt"))
    show("Generated artifact", parse(ARTIFACT_DIR / "kernel_build.artifact"))
    show("Benchmark report", parse(REPORT_DIR / "benchmark.txt"))
    print("\n[Build history]")
    history = LOG_DIR / "build-history.log"
    if history.exists():
        print(history.read_text())
    print("\n[Diagnostic status]")
    if not (BUILD_DIR / "resolved_config.txt").exists():
        print("STATUS=NOT_BUILT")
    elif not (BUILD_DIR / "execution_plan.txt").exists():
        print("STATUS=PLAN_MISSING")
    elif not (ARTIFACT_DIR / "kernel_build.artifact").exists():
        print("STATUS=ARTIFACT_MISSING")
    elif not (REPORT_DIR / "benchmark.txt").exists():
        print("STATUS=BENCHMARK_NOT_RUN")
    else:
        print("STATUS=INSPECTION_COMPLETE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
