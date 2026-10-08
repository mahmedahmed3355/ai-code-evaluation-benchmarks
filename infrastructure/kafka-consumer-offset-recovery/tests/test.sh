#!/bin/bash
set -euo pipefail
python3 -m pytest /tests/test_outputs.py /tests/test_hidden.py -q
mkdir -p /logs/verifier
echo 1 > /logs/verifier/reward.txt
