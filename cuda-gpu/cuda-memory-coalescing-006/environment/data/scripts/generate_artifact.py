import hashlib
from pathlib import Path

ROOT = Path("/app")
CONFIG = ROOT / "build" / "resolved_config.txt"
PROVENANCE = ROOT / "build" / "config_provenance.txt"
PLAN = ROOT / "build" / "execution_plan.txt"
ARTIFACT = ROOT / "artifacts" / "kernel_build.artifact"

def parse(path):
    values = {}
    for line in path.read_text().splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values

def main():
    cfg = parse(CONFIG)
    provenance = parse(PROVENANCE)
    plan = parse(PLAN)
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "BLOCK_SIZE": cfg["BLOCK_SIZE"],
        "VECTOR_WIDTH": cfg["VECTOR_WIDTH"],
        "COALESCED_ACCESS": cfg["COALESCED_ACCESS"],
        "ALIGNED_ACCESS": cfg["ALIGNED_ACCESS"],
        "FAST_PATH": cfg["FAST_PATH"],
        "CHUNK_SIZE": cfg["CHUNK_SIZE"],
        "TOTAL_WORK_UNITS": plan["TOTAL_WORK_UNITS"],
    }

    for index in range(1, 4):
        output[f"WORKLOAD_{index}_NAME"] = plan[f"WORKLOAD_{index}_NAME"]
        output[f"WORKLOAD_{index}_INPUT_SIZE"] = plan[f"WORKLOAD_{index}_INPUT_SIZE"]
        output[f"WORKLOAD_{index}_WORK_UNITS"] = plan[f"WORKLOAD_{index}_WORK_UNITS"]

    with ARTIFACT.open("w") as f:
        for key in sorted(output):
            f.write(f"{key}={output[key]}\n")

    digest = hashlib.sha256(
        (CONFIG.read_bytes() + PROVENANCE.read_bytes() + PLAN.read_bytes())
    ).hexdigest()
    (ARTIFACT.parent / "kernel_build.provenance").write_text(
        f"CONFIG_PLAN_SHA256={digest}\n"
    )

if __name__ == "__main__":
    main()
