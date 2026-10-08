#!/usr/bin/env bash
set -u
python3 -m pip install --disable-pip-version-check --no-cache-dir pytest==8.4.1 pyyaml==6.0.2 >/dev/null
python3 -m pytest /tests/test_outputs.py /tests/hidden_tests.py -rA
status=$?
mkdir -p /logs/verifier
echo $([ "$status" -eq 0 ] && echo 1 || echo 0) > /logs/verifier/reward.txt
exit "$status"
