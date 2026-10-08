#!/bin/sh
set -eu
mkdir -p /output
PYTHONPATH=/app python -c "from ml_promo.pipeline import run_promotion; run_promotion('/app/data/events.csv','/app/data/schema.json','/output/promotion.json')"
