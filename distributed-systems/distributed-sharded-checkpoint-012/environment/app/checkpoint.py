from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class ShardedCheckpoint:
    def __init__(self, root: str | Path, world_size: int):
        self.root = Path(root)
        self.world_size = world_size
        self.root.mkdir(parents=True, exist_ok=True)

    def _step_dir(self, step: int) -> Path:
        return self.root / f"step-{step}"

    def write_rank_shard(self, step: int, rank: int, state: dict[str, Any]) -> Path:
        d = self._step_dir(step)
        d.mkdir(parents=True, exist_ok=True)
        final = d / f"rank-{rank}.json"
        tmp = d / f".rank-{rank}.json.tmp"
        tmp.write_text(json.dumps(state, sort_keys=True) + "\n")
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp, final)
        return final

    def commit(self, step: int) -> Path:
        d = self._step_dir(step)
        expected = {f"rank-{r}.json" for r in range(self.world_size)}
        actual = {p.name for p in d.glob("rank-*.json") if p.is_file()}
        if actual != expected:
            raise RuntimeError("cannot commit incomplete or unexpected checkpoint shards")
        for name in sorted(expected):
            try:
                payload = json.loads((d / name).read_text())
            except Exception as exc:
                raise RuntimeError("invalid checkpoint shard") from exc
            if not isinstance(payload, dict):
                raise RuntimeError("invalid checkpoint shard")
        manifest = {"step": step, "world_size": self.world_size, "shards": sorted(expected)}
        tmp = d / ".manifest.json.tmp"
        tmp.write_text(json.dumps(manifest, sort_keys=True) + "\n")
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp, d / "manifest.json")
        return d / "manifest.json"

    def _valid_step(self, step: int, d: Path) -> bool:
        try:
            manifest = json.loads((d / "manifest.json").read_text())
            if manifest.get("step") != step or manifest.get("world_size") != self.world_size:
                return False
            expected = {f"rank-{r}.json" for r in range(self.world_size)}
            names = manifest.get("shards")
            if set(names or []) != expected or len(names or []) != self.world_size:
                return False
            actual = {p.name for p in d.glob("rank-*.json") if p.is_file()}
            if actual != expected:
                return False
            for name in expected:
                payload = json.loads((d / name).read_text())
                if not isinstance(payload, dict):
                    return False
            return True
        except Exception:
            return False

    def recover_latest(self) -> dict[str, Any] | None:
        steps = []
        for d in self.root.glob("step-*"):
            if d.is_dir():
                try:
                    steps.append((int(d.name.split("-")[1]), d))
                except (IndexError, ValueError):
                    continue
        for step, d in sorted(steps, reverse=True):
            if not self._valid_step(step, d):
                continue
            manifest = json.loads((d / "manifest.json").read_text())
            result = {name: json.loads((d / name).read_text()) for name in manifest["shards"]}
            return {"step": step, "world_size": manifest["world_size"], "shards": result}
        return None
