#!/bin/sh
set -eu
python /app/tests/test_outputs.py
python /app/tests/hidden_tests.py
python /app/tests/verify.py
