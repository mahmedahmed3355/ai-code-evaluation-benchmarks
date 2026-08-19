from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FROM_RE = re.compile(
    r"^\s*FROM\s+(?:--platform=\S+\s+)?([^\s]+)",
    re.IGNORECASE,
)

PIP_INSTALL_RE = re.compile(
    r"\bpip(?:3)?\s+install\b(.*)",
    re.IGNORECASE,
)

CONTINUATION_RE = re.compile(r"\\\s*$")


def is_pinned_image(image: str) -> bool:
    if image.lower() == "scratch":
        return True

    if "@sha256:" in image:
        return True

    name = image.split("@", 1)[0]
    last = name.rsplit("/", 1)[-1]

    return ":" in last


def docker_instructions(text: str) -> list[str]:
    """Return logical Dockerfile instructions, excluding heredoc contents."""
    instructions: list[str] = []
    lines = text.splitlines()

    current: list[str] = []
    heredoc_delimiter: str | None = None

    for line in lines:
        stripped = line.strip()

        if heredoc_delimiter is not None:
            if stripped == heredoc_delimiter:
                heredoc_delimiter = None
            continue

        if not current:
            if stripped.startswith("<<"):
                heredoc_delimiter = stripped[2:].strip("'\"")
                continue

            current.append(line)
        else:
            current.append(line)

        if CONTINUATION_RE.search(line):
            continue

        instruction = "\n".join(current)
        current = []

        if "<<" in instruction:
            marker = instruction.rsplit("<<", 1)[1].strip()
            marker = marker.split()[0].strip("'\"")
            if marker:
                heredoc_delimiter = marker

        instructions.append(instruction)

    if current:
        instructions.append("\n".join(current))

    return instructions


def pip_install_has_unpinned_package(command: str) -> bool:
    """Return True when a pip install command contains an unpinned package."""
    normalized = command.replace("\\\n", " ")

    match = re.search(
        r"\bpip(?:3)?\s+install\s+(.+)",
        normalized,
    )
    if not match:
        return False

    remainder = match.group(1)

    tokens = [
        token
        for token in remainder.split()
        if token and token != "\\"
    ]

    index = 0

    while index < len(tokens):
        token = tokens[index]

        if token in {"&&", ";"}:
            break

        if token in {"-r", "--requirement", "-c", "--constraint"}:
            return False

        if token.startswith("-r") or token.startswith("--requirement="):
            return False

        if token.startswith("-c") or token.startswith("--constraint="):
            return False

        if token.startswith("-"):
            index += 1
            continue

        if token == ".":
            index += 1
            continue

        if "==" not in token and "@git+" not in token and "@http" not in token:
            return True

        index += 1

    return False

def main() -> int:
    dockerfiles = sorted(
        path
        for path in ROOT.rglob("Dockerfile")
        if ".git" not in path.parts and ".venv" not in path.parts
    )

    unpinned_images: list[str] = []
    unpinned_pip: list[str] = []

    for dockerfile in dockerfiles:
        relative = dockerfile.relative_to(ROOT)
        text = dockerfile.read_text(encoding="utf-8")

        for instruction in docker_instructions(text):
            lines = instruction.splitlines()

            if not lines:
                continue

            first_line = lines[0]

            from_match = FROM_RE.match(first_line)
            if from_match and not is_pinned_image(from_match.group(1)):
                unpinned_images.append(
                    f"{relative}: {from_match.group(1)}"
                )

            if pip_install_has_unpinned_package(instruction):
                unpinned_pip.append(str(relative))

    print(f"Scanned Dockerfiles: {len(dockerfiles)}")

    if unpinned_images:
        print("\nUnpinned base images:")
        for item in unpinned_images:
            print(f"  - {item}")

    if unpinned_pip:
        print("\nPotential unpinned pip installs:")
        for item in unpinned_pip:
            print(f"  - {item}")

    if unpinned_images or unpinned_pip:
        print("\nDependency pinning check failed.")
        return 1

    print("All task dependency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
