import tempfile
from pathlib import Path
import test_outputs
import hidden_tests


def run(fn):
    with tempfile.TemporaryDirectory() as td:
        fn(Path(td))


cases = [
    test_outputs.test_complete_checkpoint_recovers,
    test_outputs.test_newer_incomplete_does_not_hide_older,
    test_outputs.test_extra_shard_invalidates_checkpoint,
    test_outputs.test_corrupt_shard_invalidates_checkpoint,
    test_outputs.test_manifest_cannot_claim_wrong_world_size,
    hidden_tests.test_manifest_subset_is_rejected,
    hidden_tests.test_newer_corrupt_falls_back_to_older,
    hidden_tests.test_stale_manifest_cannot_commit_partial_state,
    hidden_tests.test_payload_is_not_hardcoded,
]

for case in cases:
    run(case)
    print(f"PASS {case.__name__}")
print(f"TESTS={len(cases)} PASS")
