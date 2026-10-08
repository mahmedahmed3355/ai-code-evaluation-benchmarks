#!/bin/bash
set -euo pipefail
python tests/test_outputs.py
python tests/verify.py
python tests/hidden_tests.py
