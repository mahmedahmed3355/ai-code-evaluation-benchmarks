#!/bin/bash
set -euo pipefail
cat > /app/configs/local.override <<'CONFIG'
# Restored production memory lifecycle.
ALLOCATOR=async_pool
MEMORY_POOL=1
STREAM_ORDERED=1
REUSE=1
SYNC_MODE=event
POOL_CHUNK_SIZE=4096
MAX_POOL_BLOCKS=64
ALLOCATION_BATCH=8
CONFIG
/app/scripts/validate.sh
