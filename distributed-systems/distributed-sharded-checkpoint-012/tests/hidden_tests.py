import json
from app.checkpoint import ShardedCheckpoint


def make_complete(root, step, world):
    c = ShardedCheckpoint(root, world)
    for r in range(world):
        c.write_rank_shard(step, r, {"rank": r, "weights": [step, r, 101], "metadata": {"tag": "opaque"}})
    c.commit(step)
    return c


def test_manifest_subset_is_rejected(tmp_path):
    c = make_complete(tmp_path, 7, 3)
    p = tmp_path / "step-7" / "manifest.json"
    p.write_text(json.dumps({"step":7,"world_size":3,"shards":["rank-0.json","rank-1.json","rank-1.json"]}))
    assert c.recover_latest() is None


def test_newer_corrupt_falls_back_to_older(tmp_path):
    c = make_complete(tmp_path, 5, 4)
    for r in range(4):
        c.write_rank_shard(9, r, {"rank": r, "weights": [9, r]})
    c.commit(9)
    (tmp_path / "step-9" / "rank-2.json").write_text('{')
    got = c.recover_latest()
    assert got["step"] == 5


def test_stale_manifest_cannot_commit_partial_state(tmp_path):
    c = make_complete(tmp_path, 3, 2)
    d = tmp_path / "step-8"
    d.mkdir()
    (d / "rank-0.json").write_text(json.dumps({"rank":0}))
    (d / "manifest.json").write_text(json.dumps({"step":8,"world_size":2,"shards":["rank-0.json","rank-1.json"]}))
    assert c.recover_latest()["step"] == 3


def test_payload_is_not_hardcoded(tmp_path):
    c = make_complete(tmp_path, 88, 2)
    got = c.recover_latest()
    assert got["shards"]["rank-0.json"]["weights"] == [88, 0, 101]
    assert got["shards"]["rank-1.json"]["metadata"] == {"tag":"opaque"}
