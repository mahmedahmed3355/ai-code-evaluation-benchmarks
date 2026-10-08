from pathlib import Path
ROOT = Path("/app")
for path in sorted((ROOT / "configs").glob("*")):
    print(f"[CONFIG] {path.name}")
    print(path.read_text().strip())
for path in [
    ROOT / "build" / "resolved_config.txt",
    ROOT / "build" / "config_provenance.txt",
    ROOT / "build" / "execution_plan.txt",
    ROOT / "artifacts" / "kernel_build.artifact",
    ROOT / "artifacts" / "kernel_build.provenance",
    ROOT / "reports" / "benchmark.txt",
]:
    print(f"[OUTPUT] {path}")
    if path.exists():
        print(path.read_text().strip())
