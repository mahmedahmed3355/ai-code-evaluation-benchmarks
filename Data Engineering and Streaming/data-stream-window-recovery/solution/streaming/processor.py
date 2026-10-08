import json
from pathlib import Path
from datetime import datetime


def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()

def window_start(ts, size): return int(ts // size) * size

def atomic_write(path, obj):
    p=Path(path); tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(obj,sort_keys=True,indent=2)); tmp.replace(p)

def process(events_path, state_path, checkpoint_path, output_path, dlq_path, config_path):
    cfg=json.loads(Path(config_path).read_text())
    size=int(cfg['window_seconds']); lateness=int(cfg['allowed_lateness_seconds'])
    if size <= 0 or lateness < 0: raise ValueError('invalid streaming configuration')
    state=json.loads(Path(state_path).read_text())
    checkpoint=json.loads(Path(checkpoint_path).read_text())
    seen=set(state.get('seen_event_ids', []))
    windows=state.get('windows', {})
    finalized=set(state.get('finalized_windows', []))
    max_event_ts=state.get('max_event_ts')
    committed=int(checkpoint.get('committed_offset', -1))
    if committed < -1 or committed >= 10**9: raise ValueError('invalid checkpoint')
    # Recovery invariant: an offset may only be trusted if it belongs to the same state generation.
    if checkpoint.get('last_commit_kind') != 'state_then_offset':
        raise ValueError('checkpoint is not durable-state ordered')
    events=[json.loads(x) for x in Path(events_path).read_text().splitlines() if x.strip()]
    if committed >= len(events): raise ValueError('checkpoint is ahead of source log')
    dlq=[]
    if Path(dlq_path).exists() and Path(dlq_path).read_text().strip():
        dlq=[json.loads(x) for x in Path(dlq_path).read_text().splitlines() if x.strip()]
    for idx,e in enumerate(events):
        if idx <= committed: continue
        for required in ('event_id','event_time','key','value'):
            if required not in e: raise ValueError(f'malformed event: {required}')
        eid=e['event_id']; ets=parse_ts(e['event_time'])
        # At-least-once delivery: stable event identity, not transport metadata, defines uniqueness.
        if eid in seen:
            continue
        if max_event_ts is None or ets > max_event_ts: max_event_ts=ets
        watermark=max_event_ts-lateness
        ws=str(window_start(ets,size))
        if ws in finalized:
            dlq.append({'event_id':eid,'reason':'late_after_finalization','window_start':ws,'event_time':e['event_time'],'offset':idx})
            seen.add(eid)
            next_state={'seen_event_ids':sorted(seen),'windows':windows,'finalized_windows':sorted(finalized,key=int),'max_event_ts':max_event_ts}
            atomic_write(state_path,next_state)
            checkpoint['committed_offset']=idx; checkpoint['last_commit_kind']='state_then_offset'; checkpoint['generation']=int(checkpoint.get('generation',0))+1
            atomic_write(checkpoint_path,checkpoint)
            continue
        w=windows.setdefault(ws, {'count':0,'sum':0.0,'by_key':{}})
        w['count'] += 1; w['sum'] += float(e['value'])
        w['by_key'][e['key']] = w['by_key'].get(e['key'],0.0) + float(e['value'])
        seen.add(eid)
        # Finalize every eligible window, but never reopen a finalized window.
        for candidate in list(windows):
            if int(candidate) + size <= watermark:
                finalized.add(candidate)
        # Simulate durable commit after state transition. Checkpoint is only advanced after the
        # state has been made internally consistent; atomic writes make restart idempotent.
        next_state={'seen_event_ids':sorted(seen),'windows':windows,'finalized_windows':sorted(finalized,key=int),'max_event_ts':max_event_ts}
        atomic_write(state_path,next_state)
        checkpoint['committed_offset']=idx; checkpoint['last_commit_kind']='state_then_offset'; checkpoint['generation']=int(checkpoint.get('generation',0))+1
        atomic_write(checkpoint_path,checkpoint)
    # Final pass: output is a pure projection of durable state, so rerunning is re-entrant.
    out=[]
    for ws in sorted(finalized,key=int):
        w=windows[ws]
        out.append({'window_start':ws,'count':w['count'],'sum':round(w['sum'],6),'by_key':{k:round(v,6) for k,v in sorted(w['by_key'].items())}})
    atomic_write(output_path,out)
    Path(dlq_path).write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in dlq))
    return state,checkpoint
