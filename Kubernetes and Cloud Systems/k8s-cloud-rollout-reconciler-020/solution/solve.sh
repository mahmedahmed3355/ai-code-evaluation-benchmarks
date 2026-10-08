#!/bin/sh
set -eu
python /solution/reference_impl.py --spec /app/data/spec.json --state /app/data/cluster_state.json --out /app/out.json
