import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path("/app/data")
CONFIG=ROOT/"allocator_config.json"
WORKLOADS=ROOT/"workloads.json"
VALIDATOR=ROOT/"validate_allocator.py"

EXPECTED_VALIDATOR_SHA = "ca1644d22cb0e25ae9a77018a6fc0c0de4ebc87b2704f35bffc5ceed6a555326"
EXPECTED_WORKLOADS_SHA = "8b9d87429f2d61220660c742b789bfe28d69d42e67c58cfb8558c25c849ac789"
EXPECTED_NAMES = {
    "embedding_batch": (0, 131072, "cross_stream"),
    "attention_workspace": (1, 196608, "cross_stream"),
    "vision_workspace": (0, 98304, "deferred"),
    "reduction_workspace": (1, 65536, "deferred"),
}

def load(path):
    assert path.exists(), f"Missing required file: {path}"
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def test_required_files_and_independent_validator_are_intact():
    assert CONFIG.exists() and WORKLOADS.exists() and VALIDATOR.exists()
    assert sha(VALIDATOR) == EXPECTED_VALIDATOR_SHA
    assert sha(WORKLOADS) == EXPECTED_WORKLOADS_SHA

def test_async_allocator_contract():
    result = subprocess.run(["python3", str(VALIDATOR)], capture_output=True, text=True)
    assert result.returncode == 0, f"validator failed:\n{result.stdout}\n{result.stderr}"

def test_effective_async_pool_semantics():
    d=load(CONFIG); a=d["allocator"]; e=d["execution"]
    assert a["api"]=="cudaMallocAsync"
    assert a["free_api"]=="cudaFreeAsync"
    assert a["memory_pool"] is True
    assert a["stream_ordered_free"] is True
    assert a["deferred_release"] is True
    assert a["cross_stream_events"] is True
    assert isinstance(a["release_threshold"], int) and a["release_threshold"] > 0
    assert e["streams"] == 2
    assert e["synchronize_before_release"] is True

def test_memory_policy_is_preserved():
    d=load(CONFIG)
    assert d["policy"] == {"max_live_bytes":524288, "max_deferred_bytes":262144}
    assert d["incident"] == {
        "id":"CUDA-ALLOC-008",
        "status":"regression",
        "introduced_by":"runtime-memory-config-2026-10-01",
    }

def test_supported_workloads_are_exactly_preserved():
    w=load(WORKLOADS)["workloads"]
    assert len(w)==4
    assert {x["name"] for x in w} == set(EXPECTED_NAMES)
    for x in w:
        assert (x["stream"],x["bytes"],x["lifetime"]) == EXPECTED_NAMES[x["name"]]

def test_no_legacy_synchronous_allocator():
    d=load(CONFIG); a=d["allocator"]
    assert a["api"] != "cudaMalloc"
    assert a["free_api"] != "cudaFree"

def test_cross_stream_workloads_require_events():
    w=load(WORKLOADS)["workloads"]; a=load(CONFIG)["allocator"]
    assert any(x["lifetime"]=="cross_stream" for x in w)
    assert a["cross_stream_events"] is True
    assert a["stream_ordered_free"] is True
