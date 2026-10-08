#!/usr/bin/env python3
from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
BUILD_DIR = ROOT / "build"
ARTIFACT_DIR = ROOT / "artifacts"
REFERENCE = ROOT / "reference" / "optimization_contract.txt"

SOURCES = (
    "build.conf",
    "release.profile",
    "benchmark.conf",
    "local.override",
)


def parse(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


def main() -> int:
    print("=== GPU BUILD DIAGNOSTIC ===")
    print("[Configuration sources]")
    for name in SOURCES:
        print(f"{name}={'present' if (CONFIG_DIR / name).exists() else 'missing'}")

    print("[Effective configuration]")
    effective = parse(BUILD_DIR / "effective_config.txt")
    for key in sorted(effective):
        print(f"{key}={effective[key]}")

    print("[Generated artifact]")
    artifact = parse(ARTIFACT_DIR / "kernel_build.artifact")
    for key in sorted(artifact):
        print(f"{key}={artifact[key]}")

    print("[Expected contract]")
    contract = parse(REFERENCE)
    for key in sorted(contract):
        print(f"{key}={contract[key]}")

    print("[Diagnostic status]")
    print("STATUS=INSPECTION_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
