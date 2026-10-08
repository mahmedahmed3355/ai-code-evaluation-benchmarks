#!/bin/bash
set -euo pipefail

cat > /app/configs/local.override <<'EOF'
BLOCK_SIZE=256
VECTOR_WIDTH=4
COALESCED_ACCESS=1
ALIGNED_ACCESS=1
FAST_PATH=1
CHUNK_SIZE=4096
EOF

/app/scripts/validate.sh
