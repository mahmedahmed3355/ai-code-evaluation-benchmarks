#!/usr/bin/env python3
import json
from pathlib import Path

CONFIG=Path("/app/data/stream_config.json")
WORKLOADS=Path("/app/data/workloads.json")
EXPECTED={
 "embedding_pipeline":6,"attention_pipeline":10,
 "vision_pipeline":8,"reduction_pipeline":12,
}

def main():
    c=json.loads(CONFIG.read_text())
    w=json.loads(WORKLOADS.read_text())
    assert c["streams"]=={"producer":0,"consumer":1,"finalizer":2}
    assert c["events"]["producer_completion"]=={
        "recorded":True,"event_id":"producer_done","recorded_on_stream":0}
    assert c["events"]["consumer_completion"]=={
        "recorded":True,"event_id":"consumer_done","recorded_on_stream":1}
    deps=c["dependencies"]
    assert deps==[
        {"from_stream":0,"to_stream":1,"wait_event":"producer_done"},
        {"from_stream":1,"to_stream":2,"wait_event":"consumer_done"},
    ]
    assert c["execution"]=={
        "async":True,"global_synchronize":False,"cross_stream_dependencies":True}
    assert c["dependency_contract"]=={
        "producer_must_precede_consumer":True,
        "consumer_must_precede_finalizer":True,
        "required_wait_semantics":"cross_stream_event",
    }
    got={x["name"]:x["operations"] for x in w["workloads"]}
    assert got==EXPECTED
    print("VALIDATION=PASS")
if __name__=="__main__": main()
