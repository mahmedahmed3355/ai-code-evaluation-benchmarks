"""Independent structural verifier; deliberately does not import candidate code."""
import json, os
from pathlib import Path
root=Path('/app/environment')
required=['Dockerfile','data/config.json','data/events.jsonl','data/state.json','data/checkpoint.json','data/expected_contract.json','streaming/processor.py','streaming/cli.py']
for x in required:
    assert (root/x).exists(), x
cfg=json.loads((root/'data/config.json').read_text()); contract=json.loads((root/'data/expected_contract.json').read_text())
assert cfg['delivery_semantics']=='at_least_once'
assert cfg['dedupe_key']=='event_id'
assert contract['checkpoint_order']=='state_then_offset'
assert contract['dedupe']=='event_id'
assert contract['watermark']=='max_event_time_minus_allowed_lateness'
assert contract['late_policy']=='dead_letter_if_finalized'
src=(root/'streaming/processor.py').read_text()
# Baseline must contain the intended anti-patterns; otherwise the benchmark is not a repair task.
for marker in ['delivery_duplicate','committed_offset','finalized_windows','max_event_ts']:
    assert marker in src
print('independent structural verification: PASS')
