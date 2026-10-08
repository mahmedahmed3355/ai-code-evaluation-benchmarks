# Verification suite

`test_outputs.py` contains the visible contract checks used by the task
harness. `hidden_tests.py` contains adversarial cross-resource checks that
should be treated as verifier-only checks in benchmark execution.

The tests intentionally validate relationships between resources rather than
accepting a single edited value.
