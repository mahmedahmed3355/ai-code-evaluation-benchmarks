"""Independent behavioral verifier used by benchmark harnesses."""
import json
from pathlib import Path
from app.checkpoint import ShardedCheckpoint


def write_complete(root, step, world, token):
    c = ShardedCheckpoint(root, world)
    for rank in range(world):
        c.write_rank_shard(step, rank, {"token": token, "rank": rank})
    c.commit(step)
    return c


def verify_recovery(root):
    c = write_complete(root, 31, 3, "alpha")
    newer = root / "step-44"
    newer.mkdir()
    (newer / "rank-0.json").write_text(json.dumps({"token": "beta", "rank": 0}))
    (newer / "manifest.json").write_text(json.dumps({
        "step": 44,
        "world_size": 3,
        "shards": ["rank-0.json", "rank-1.json", "rank-2.json"],
    }))
    result = c.recover_latest()
    assert result["step"] == 31
    assert result["shards"]["rank-2.json"]["token"] == "alpha"


def main():
    root = Path("/tmp/verifier-check")
    import shutil
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir()
    verify_recovery(root)
    print("VERIFIER=PASS")


if __name__ == "__main__":
    main()
