#!/bin/sh
set -eu
pytest -q /app/tests/test_outputs.py /app/tests/hidden_tests.py
