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
    print(path.read_text().strip())

print()
print("[Effective configuration]")

resolved = ROOT / "build" / "resolved_config.txt"

if resolved.exists():
    print(resolved.read_text().strip())
else:
    print("resolved configuration not generated")

print()
print("[Execution plan]")

plan = ROOT / "build" / "execution_plan.txt"

if plan.exists():
    print(plan.read_text().strip())
else:
    print("execution plan not generated")

print()
print("[Generated artifact]")

artifact = ROOT / "artifacts" / "kernel_build.artifact"

if artifact.exists():
    print(artifact.read_text().strip())
else:
    print("artifact not generated")

print()
print("[Benchmark report]")

report = ROOT / "reports" / "benchmark.txt"

if report.exists():
    print(report.read_text().strip())
else:
    print("benchmark report not generated")
