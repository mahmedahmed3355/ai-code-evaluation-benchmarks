#!/usr/bin/env python3

from pathlib import Path

ROOT = Path("/app")
CONFIG_DIR = ROOT / "configs"
OUTPUT = ROOT / "build" / "resolved_config.txt"


def load_config(path: Path) -> dict[str, str]:
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


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    config = {}

    # Base contract.
    config.update(load_config(CONFIG_DIR / "build.conf"))

    # Selected release profile.
    config.update(load_config(CONFIG_DIR / "release.profile"))

    # Benchmark-specific requirements.
    config.update(load_config(CONFIG_DIR / "benchmark.conf"))

    # Compatibility settings are intentionally loaded last.
    #
    # The task's regression is related to how configuration sources
    # are resolved. Investigate the resulting effective state rather
    # than assuming every source has the same precedence.
    config.update(load_config(CONFIG_DIR / "local.override"))

    OUTPUT.write_text(
        "".join(
            f"{key}={value}\n"
            for key, value in sorted(config.items())
        )
    )

    print(f"Resolved configuration written to {OUTPUT}")

    for key in sorted(config):
        print(f"{key}={config[key]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
