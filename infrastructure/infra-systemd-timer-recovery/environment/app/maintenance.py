import json
from pathlib import Path

def run(job_generation: str, mode: str, state_dir: str):
    state = Path(state_dir)
    state.mkdir(parents=True, exist_ok=True)
    result = {"job_generation": job_generation, "mode": mode}
    if mode == "fail":
        (state / "last_result.json").write_text(json.dumps({
            **result, "status": "failed"
        }))
        raise RuntimeError("maintenance failure")
    (state / "last_result.json").write_text(json.dumps({
        **result, "status": "success"
    }))
    return result
