from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
OUT = ROOT / "build" / "resolved_config.txt"
PROVENANCE = ROOT / "build" / "config_provenance.txt"

FILES = [
    CONFIG_DIR / "build.conf",
    CONFIG_DIR / "release.profile",
    CONFIG_DIR / "benchmark.conf",
    CONFIG_DIR / "local.override",
]

def parse(path):
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values

def main():
    resolved = {}
    source = {}
    for path in FILES:
        for key, value in parse(path).items():
            resolved[key] = value
            source[key] = path.name

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={resolved[key]}\n")

    with PROVENANCE.open("w") as f:
        for key in sorted(resolved):
            f.write(f"{key}={source[key]}\n")

if __name__ == "__main__":
    main()
