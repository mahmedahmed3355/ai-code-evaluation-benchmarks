import json
from pathlib import Path
from datetime import datetime, timezone


def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()

def window_start(ts, size):
    return int(ts // size) * size

def process(events_path, state_path, checkpoint_path, output_path, dlq_path, config_path):
    cfg=json.loads(Path(config_path).read_text())
    size=int(cfg['window_seconds']); lateness=int(cfg['allowed_lateness_seconds'])
    state=json.loads(Path(state_path).read_text())
    checkpoint=json.loads(Path(checkpoint_path).read_text())
    # BROKEN: checkpoint offset is treated as an inclusive event index and state is rebuilt
    # without preserving the event-id deduplication set. Watermark is also based on wall clock
    # order rather than event time, and late/finalized windows can be mutated after emission.
    seen=set(state.get('seen_event_ids', []))
    windows=state.get('windows', {})
    finalized=set(state.get('finalized_windows', []))
    max_event_ts=state.get('max_event_ts')
    committed=int(checkpoint.get('committed_offset', -1))
    events=[json.loads(x) for x in Path(events_path).read_text().splitlines() if x.strip()]
    for idx,e in enumerate(events):
        if idx <= committed: continue
        eid=e['event_id']; ets=parse_ts(e['event_time'])
        # broken duplicate semantics: dedupe by offset instead of stable event id
        if e.get('delivery_duplicate', False):
            continue
        if max_event_ts is None or ets > max_event_ts: max_event_ts=ets
        ws=str(window_start(ets,size))
        watermark=max_event_ts-lateness
        if ws in finalized:
            # broken: mutate finalized aggregate instead of routing late data to DLQ
            pass
        w=windows.setdefault(ws, {'count':0,'sum':0.0,'by_key':{}})
        w['count']+=1; w['sum']+=float(e['value'])
        k=e['key']; w['by_key'][k]=w['by_key'].get(k,0)+float(e['value'])
        seen.add(eid)
        # broken: finalize before all events at the watermark boundary have been examined
        if ets <= watermark: finalized.add(ws)
        checkpoint['committed_offset']=idx
    state.update({'seen_event_ids':sorted(seen),'windows':windows,'finalized_windows':sorted(finalized),'max_event_ts':max_event_ts})
    Path(state_path).write_text(json.dumps(state,sort_keys=True,indent=2))
    Path(checkpoint_path).write_text(json.dumps(checkpoint,sort_keys=True,indent=2))
    out=[]
    for ws in sorted(finalized,key=lambda x:int(x)):
        if ws in windows:
            out.append({'window_start':ws,'count':windows[ws]['count'],'sum':round(windows[ws]['sum'],6),'by_key':windows[ws]['by_key']})
    Path(output_path).write_text(json.dumps(out,sort_keys=True,indent=2))
    if not Path(dlq_path).exists(): Path(dlq_path).write_text('')
    return state,checkpoint
