#!/bin/bash
set -euo pipefail

CONFIG="/app/configs/local.override"

cat > "$CONFIG" <<'CONFIG'
# Optimized stream-ordered memory pool configuration.
ALLOCATOR=async_pool
MEMORY_POOL=1
STREAM_ORDERED=1
REUSE=1
SYNC_MODE=event
POOL_CHUNK_SIZE=4096
MAX_POOL_BLOCKS=64
ALLOCATION_BATCH=8
CONFIG

echo "Restored optimized stream-ordered memory pool configuration."

/app/scripts/validate.sh
