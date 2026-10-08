#!/bin/sh
set -eu
python /app/tests/test_runner.py
python /app/tests/verify.py
