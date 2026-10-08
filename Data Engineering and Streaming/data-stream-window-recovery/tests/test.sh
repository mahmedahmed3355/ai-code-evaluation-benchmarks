#!/bin/sh
set -eu
cd /app
rm -rf /app/streaming
cp -r /app/solution/streaming /app/streaming
pytest -q /app/tests/test_outputs.py /app/tests/hidden_tests.py
python /app/tests/verify.py
