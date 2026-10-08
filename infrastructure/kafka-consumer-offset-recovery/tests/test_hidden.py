import json
from pathlib import Path
R=Path("/app/data")
def L(n): return json.loads((R/n).read_text())

def test_hidden_partial_progress_cannot_be_recovered():
    s=L("recovery_state.json")["partitions"]["0"]
    assert s["processed_offset"] > s["committed_offset"]
    assert s["last_recovered_offset"] < s["processed_offset"]

def test_hidden_journal_is_authoritative():
    j=L("commit_journal.json"); r=L("recovery_state.json")
    m={str(x["partition"]):x["offset"] for x in j["commits"]}
    assert {p:s["last_recovered_offset"] for p,s in r["partitions"].items()} == m

def test_hidden_rebalance_matches_recovery():
    rb=L("rebalance_state.json"); r=L("recovery_state.json")
    assert rb["active_generation"]==r["generation"]
    assert rb["active_assignment_epoch"]==r["assignment_epoch"]

def test_hidden_checkpoint_has_exact_partition_set():
    assert set(L("recovery_state.json")["checkpoint"]["offsets"]) == {"0","1"}
