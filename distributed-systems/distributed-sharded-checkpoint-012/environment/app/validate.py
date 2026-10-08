from pathlib import Path
from .checkpoint import ShardedCheckpoint


def seed_fixture(root: Path) -> None:
    ckpt = ShardedCheckpoint(root, world_size=2)
    ckpt.write_rank_shard(10, 0, {"loss": 0.40, "tokens": 1000, "weights": [1, 2]})
    ckpt.write_rank_shard(10, 1, {"loss": 0.41, "tokens": 980, "weights": [3, 4]})
    ckpt.commit(10)

    # A newer step is intentionally incomplete. It represents a crashed commit.
    ckpt.write_rank_shard(20, 0, {"loss": 0.30, "tokens": 1200, "weights": [5, 6]})
    (root / "step-20" / "manifest.json").write_text(
        '{"step":20,"world_size":2,"shards":["rank-0.json","rank-1.json"]}\n'
    )


def validate(root: Path) -> None:
    if root.exists():
        import shutil
        shutil.rmtree(root)
    root.mkdir(parents=True)
    seed_fixture(root)
    ckpt = ShardedCheckpoint(root, 2)
    recovered = ckpt.recover_latest()
    if recovered is None or recovered["step"] != 10:
        raise AssertionError(f"expected step 10, got {recovered}")
    print("VALIDATION=PASS")

if __name__ == "__main__":
    import sys
    validate(Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/checkpoints"))
