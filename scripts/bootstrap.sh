#!/usr/bin/env bash

set -euo pipefail

uv sync --group dev --locked
uv run pytest tests/ -v
