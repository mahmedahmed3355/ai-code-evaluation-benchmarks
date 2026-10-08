#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")

print("[Configuration sources]")

for path in sorted((ROOT / "configs").glob("*")):
    print(f"- {path}")

print()
print("[Configuration provenance]")

for path in [
    ROOT / "configs" / "build.conf",
    ROOT / "configs" / "release.profile",
    ROOT / "configs" / "benchmark.conf",
    ROOT / "configs" / "local.override",
]:
    print(f"\n--- {path.name} ---")
    if path.exists():
        print(path.read_text(), end="")

print()
print("[Effective configuration]")

resolved = ROOT / "build" / "resolved_config.txt"

if resolved.exists():
    print(resolved.read_text(), end="")
else:
    print("resolved configuration has not been generated")

print()
print("[Execution plan]")

plan = ROOT / "build" / "execution_plan.txt"

if plan.exists():
    print(plan.read_text(), end="")
else:
    print("execution plan has not been generated")

print()
print("[Generated artifact]")

artifact = ROOT / "artifacts" / "kernel_build.artifact"

if artifact.exists():
    print(f"path={artifact}")
    print(f"size={artifact.stat().st_size}")
else:
    print("artifact has not been generated")

print()
print("[Benchmark report]")

report = ROOT / "reports" / "benchmark.txt"

if report.exists():
    print(report.read_text(), end="")
else:
    print("benchmark report has not been generated")
