#!/bin/sh
set -eu
cp /solution/ml_service/*.py /app/ml_service/
python /app/tests/test_outputs.py
python /app/tests/hidden_tests.py
python /app/tests/verify.py
