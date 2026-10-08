import json
from pathlib import Path
from app.checkpoint import ShardedCheckpoint


def complete(root, step=10, world=2, payload_offset=0):
    c = ShardedCheckpoint(root, world)
    for r in range(world):
        c.write_rank_shard(step, r, {"rank": r, "value": payload_offset + r, "opaque": [7, 11, 19]})
    c.commit(step)
    return c


def test_complete_checkpoint_recovers(tmp_path):
    c = complete(tmp_path, 42, 3, 100)
    got = c.recover_latest()
    assert got["step"] == 42
    assert set(got["shards"]) == {"rank-0.json", "rank-1.json", "rank-2.json"}


def test_newer_incomplete_does_not_hide_older(tmp_path):
    c = complete(tmp_path, 10, 2)
    c.write_rank_shard(20, 0, {"value": "new"})
    d = tmp_path / "step-20"
    d.joinpath("manifest.json").write_text(json.dumps({"step":20,"world_size":2,"shards":["rank-0.json","rank-1.json"]}))
    assert c.recover_latest()["step"] == 10


def test_extra_shard_invalidates_checkpoint(tmp_path):
    c = complete(tmp_path, 10, 2)
    (tmp_path / "step-10" / "rank-9.json").write_text('{}')
    assert c.recover_latest() is None


def test_corrupt_shard_invalidates_checkpoint(tmp_path):
    c = complete(tmp_path, 10, 2)
    (tmp_path / "step-10" / "rank-1.json").write_text('{bad')
    assert c.recover_latest() is None


def test_manifest_cannot_claim_wrong_world_size(tmp_path):
    c = complete(tmp_path, 10, 2)
    p = tmp_path / "step-10" / "manifest.json"
    p.write_text(json.dumps({"step":10,"world_size":99,"shards":["rank-0.json","rank-1.json"]}))
    assert c.recover_latest() is None
