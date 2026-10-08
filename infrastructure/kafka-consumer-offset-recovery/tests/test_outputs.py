import json
from pathlib import Path

ROOT = Path("/app/data")
CFG = ROOT/"consumer_config.json"
REC = ROOT/"recovery_state.json"
WORK = ROOT/"workloads.json"
JOURNAL = ROOT/"commit_journal.json"
REBAL = ROOT/"rebalance_state.json"

def load(p): return json.loads(p.read_text())

def test_active_assignment_is_unchanged():
    c = load(CFG); r = load(REBAL)
    assert c["consumer_group"] == "inference-workers"
    assert c["topic"] == "model-events"
    assert c["partitions"] == [0,1]
    assert c["assignment"]["partition_owner"] == {"0":"worker-a","1":"worker-a"}
    assert r["active_generation"] == c["assignment"]["generation"]
    assert r["active_assignment_epoch"] == c["assignment"]["assignment_epoch"]

def test_manual_commit_contract():
    c=load(CFG)
    assert c["processing"] == {"auto_commit":False,"enable_idempotence":True,"commit_mode":"manual"}

def test_generation_and_epoch_are_coherent():
    c=load(CFG); r=load(REC); rb=load(REBAL); j=load(JOURNAL)
    g=c["assignment"]["generation"]; e=c["assignment"]["assignment_epoch"]
    assert (r["generation"],r["assignment_epoch"]) == (g,e)
    assert (r["restart"]["recovery_generation"],r["restart"]["recovery_epoch"]) == (g,e)
    assert (r["checkpoint"]["generation"],r["checkpoint"]["assignment_epoch"]) == (g,e)
    assert (rb["active_generation"],rb["active_assignment_epoch"]) == (g,e)
    assert (j["generation"],j["assignment_epoch"]) == (g,e)

def test_recovered_offsets_equal_durable_commits():
    r=load(REC); j=load(JOURNAL)
    commits={str(x["partition"]):x["offset"] for x in j["commits"]}
    assert set(commits)=={"0","1"}
    for p,s in r["partitions"].items():
        assert s["committed_offset"] == commits[p]
        assert s["last_recovered_offset"] == commits[p]
        assert r["checkpoint"]["offsets"][p] == commits[p]
        assert s["committed_offset"] <= s["processed_offset"]

def test_processed_history_was_not_rewritten():
    r=load(REC)
    assert r["partitions"]["0"]["processed_offset"] == 124
    assert r["partitions"]["1"]["processed_offset"] == 88
    assert r["partitions"]["0"]["committed_offset"] == 120

def test_restart_policy_is_preserved():
    c=load(CFG); r=load(REC)
    assert c["recovery"]["on_restart"]=="resume_from_committed"
    assert c["recovery"]["on_rebalance"]=="preserve_committed_offsets"
    assert r["restart"]["resume_policy"]=="resume_from_committed"

def test_partition_ownership_is_preserved():
    c=load(CFG); r=load(REC)
    owners=c["assignment"]["partition_owner"]
    for p in ("0","1"):
        assert r["partitions"][p]["assigned_to"] == owners[p]

def test_durable_commit_journal_is_not_fabricated():
    j=load(JOURNAL)
    assert [(x["partition"],x["offset"]) for x in j["commits"]] == [(0,120),(1,88)]
    assert [x["committed_at_sequence"] for x in j["commits"]] == [901,902]

def test_workloads_unchanged():
    w=load(WORK)["workloads"]
    assert [x["name"] for x in w] == ["embedding_events","batch_inference","replay_recovery","streaming_updates"]
    assert [x["messages"] for x in w] == [24,32,16,20]

def test_no_destructive_reset_contract():
    c=load(CFG); r=load(REC)
    blob=json.dumps({"config":c,"recovery":r}).lower()
    for marker in ("reset_to_latest","reset_to_earliest","seek_to_end","delete_offsets","offset_reset"):
        assert marker not in blob

def test_checkpoint_source_is_restart():
    assert load(REC)["checkpoint"]["source"] == "restart"
