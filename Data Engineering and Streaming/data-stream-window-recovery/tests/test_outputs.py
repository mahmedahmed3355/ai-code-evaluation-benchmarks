import json, shutil, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT=Path('/app')
BASE=ROOT/'environment/data'
W0=str(int(datetime(2026,1,1,tzinfo=timezone.utc).timestamp())//300*300)
W1=str(int(datetime(2026,1,1,tzinfo=timezone.utc).timestamp()+300)//300*300)
W2=str(int(datetime(2026,1,1,tzinfo=timezone.utc).timestamp()+600)//300*300)

def run_case(tmp_path, events=None, state=None, checkpoint=None, config=None, solution=True, reset=True):
    if reset:
        for name in ['events.jsonl','state.json','checkpoint.json','config.json']:
            shutil.copy2(BASE/name,tmp_path/name)
    if events is not None: (tmp_path/'events.jsonl').write_text('\n'.join(json.dumps(e) for e in events)+'\n')
    if state is not None: (tmp_path/'state.json').write_text(json.dumps(state,indent=2))
    if checkpoint is not None: (tmp_path/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2))
    if config is not None: (tmp_path/'config.json').write_text(json.dumps(config,indent=2))
    if reset or not (tmp_path/'dlq.jsonl').exists(): (tmp_path/'dlq.jsonl').write_text('')
    if reset or not (tmp_path/'output.json').exists(): (tmp_path/'output.json').write_text('[]')
    env={'PYTHONPATH':'/app'}
    cmd=[sys.executable,'-m','streaming.cli','--events',str(tmp_path/'events.jsonl'),'--state',str(tmp_path/'state.json'),'--checkpoint',str(tmp_path/'checkpoint.json'),'--output',str(tmp_path/'output.json'),'--dlq',str(tmp_path/'dlq.jsonl'),'--config',str(tmp_path/'config.json')]
    if solution:
        cmd=[sys.executable,'-m','solution.streaming.cli','--events',str(tmp_path/'events.jsonl'),'--state',str(tmp_path/'state.json'),'--checkpoint',str(tmp_path/'checkpoint.json'),'--output',str(tmp_path/'output.json'),'--dlq',str(tmp_path/'dlq.jsonl'),'--config',str(tmp_path/'config.json')]
    return subprocess.run(cmd,cwd='/app',env=env,text=True,capture_output=True)

def load(p): return json.loads(p.read_text())
def base_event(i, sec, key='x', value=1):
    t=datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(seconds=sec)
    return {'event_id':i,'event_time':t.isoformat().replace('+00:00','Z'),'key':key,'value':value}

def test_nominal_contract(tmp_path):
    r=run_case(tmp_path); assert r.returncode==0,r.stderr
    s=load(tmp_path/'state.json'); c=load(tmp_path/'checkpoint.json')
    assert 'seen_event_ids' in s and 'windows' in s and 'finalized_windows' in s and 'max_event_ts' in s
    assert c['last_commit_kind']=='state_then_offset'

def test_duplicate_event_id_is_once(tmp_path):
    ev=[base_event('a',10,'x',3),base_event('a',10,'x',999),base_event('b',20,'x',2),base_event('c',700,'x',1)]
    st={'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None}
    cp={'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'}
    r=run_case(tmp_path,ev,st,cp); assert r.returncode==0,r.stderr
    assert load(tmp_path/'state.json')['windows'][W0]['sum']==5

def test_delivery_metadata_cannot_bypass_dedupe(tmp_path):
    ev=[base_event('a',10,'x',3),dict(base_event('a',10,'x',8),delivery_duplicate=True)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert load(tmp_path/'state.json')['windows'][W0]['sum']==3

def test_late_event_goes_dlq_after_finalization(tmp_path):
    ev=[base_event('a',0,'x',1),base_event('b',700,'x',2),base_event('late',10,'x',50)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    s=load(tmp_path/'state.json'); dl=[json.loads(x) for x in (tmp_path/'dlq.jsonl').read_text().splitlines()]
    assert s['windows'][W0]['sum']==1 and any(x['event_id']=='late' for x in dl)

def test_late_event_does_not_mutate_finalized_window(tmp_path):
    ev=[base_event('a',0,'x',1),base_event('b',700,'x',2),base_event('late',20,'x',99)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert load(tmp_path/'state.json')['windows'][W0]['sum']==1

def test_event_time_not_arrival_time(tmp_path):
    ev=[base_event('a',300,'x',1),base_event('b',10,'x',2),base_event('c',800,'x',3)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    s=load(tmp_path/'state.json'); assert s['windows'][W0]['sum']==2 and s['windows'][W1]['sum']==1

def test_lateness_boundary_is_allowed_before_finalization(tmp_path):
    ev=[base_event('a',0,'x',1),base_event('b',500,'x',2),base_event('c',380,'x',4)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert load(tmp_path/'state.json')['windows'][W1]['sum']==6

def test_key_aggregation(tmp_path):
    ev=[base_event('a',1,'a',2),base_event('b',2,'b',4),base_event('c',3,'a',5)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert load(tmp_path/'state.json')['windows'][W0]['by_key']=={'a':7.0,'b':4.0}

def test_resume_from_committed_offset(tmp_path):
    ev=[base_event('a',10,'x',3),base_event('b',20,'x',4),base_event('c',30,'x',5)]
    st={'seen_event_ids':['a','b'],'windows':{W0:{'count':2,'sum':7,'by_key':{'x':7}}},'finalized_windows':[],'max_event_ts':base_event('b',20)['event_time']}
    st['max_event_ts']=(datetime.fromisoformat(st['max_event_ts'].replace('Z','+00:00')).timestamp())
    cp={'committed_offset':1,'generation':2,'last_commit_kind':'state_then_offset'}
    r=run_case(tmp_path,ev,st,cp); assert r.returncode==0
    assert load(tmp_path/'state.json')['windows'][W0]['count']==3

def test_replay_after_state_ahead_of_checkpoint_is_idempotent(tmp_path):
    ev=[base_event('a',10,'x',3),base_event('b',20,'x',4)]
    st={'seen_event_ids':['a'],'windows':{W0:{'count':1,'sum':3,'by_key':{'x':3}}},'finalized_windows':[],'max_event_ts':10.0}
    cp={'committed_offset':-1,'generation':1,'last_commit_kind':'state_then_offset'}
    r=run_case(tmp_path,ev,st,cp); assert r.returncode==0
    s=load(tmp_path/'state.json'); assert s['windows'][W0]['sum']==7 and s['windows'][W0]['count']==2

def test_reentrant_second_run_same_output(tmp_path):
    r=run_case(tmp_path); assert r.returncode==0,r.stderr
    out1=tmp_path/'output.json'; first=out1.read_text(); dl1=(tmp_path/'dlq.jsonl').read_text(); st1=(tmp_path/'state.json').read_text();
    r2=run_case(tmp_path, solution=True); assert r2.returncode==0,r2.stderr
    assert out1.read_text()==first
    assert (tmp_path/'dlq.jsonl').read_text()==dl1

def test_invalid_commit_kind_fails_closed(tmp_path):
    cp={'committed_offset':2,'generation':1,'last_commit_kind':'offset_then_state'}
    r=run_case(tmp_path,checkpoint=cp); assert r.returncode!=0

def test_negative_checkpoint_fails_closed(tmp_path):
    cp={'committed_offset':-5,'generation':1,'last_commit_kind':'state_then_offset'}
    r=run_case(tmp_path,checkpoint=cp); assert r.returncode!=0

def test_invalid_window_config_fails_closed(tmp_path):
    r=run_case(tmp_path,config={'window_seconds':0,'allowed_lateness_seconds':120,'delivery_semantics':'at_least_once','aggregation':'sum_and_count','dedupe_key':'event_id'})
    assert r.returncode!=0

def test_output_only_finalized_windows(tmp_path):
    ev=[base_event('a',1,'x',1),base_event('b',301,'x',2)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert all(int(x['window_start'])+300 <= load(tmp_path/'state.json')['max_event_ts']-120 for x in load(tmp_path/'output.json'))

def test_original_event_payload_not_mutated(tmp_path):
    ev=[base_event('a',10,'x',3),base_event('b',700,'x',2)]
    raw='\n'.join(json.dumps(x) for x in ev)+'\n'
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0 and (tmp_path/'events.jsonl').read_text()==raw

def test_no_future_window_created_by_old_event(tmp_path):
    ev=[base_event('a',601,'x',1),base_event('b',2,'x',2)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert W0 in load(tmp_path/'state.json')['windows']

def test_float_values_preserved(tmp_path):
    ev=[base_event('a',1,'x',1.25),base_event('b',2,'x',2.75)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0 and load(tmp_path/'state.json')['windows'][W0]['sum']==4

def test_many_events_unique(tmp_path):
    ev=[base_event(f'e{i}',i,'k'+str(i%4),i%7+0.5) for i in range(100)]
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0
    assert sum(w['count'] for w in load(tmp_path/'state.json')['windows'].values())==100

def test_duplicate_burst(tmp_path):
    ev=[]
    for i in range(20):
        e=base_event(f'e{i}',i,'x',1); ev.extend([e,dict(e),dict(e)])
    r=run_case(tmp_path,ev,{'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None},{'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'})
    assert r.returncode==0 and load(tmp_path/'state.json')['windows'][W0]['count']==20

def test_dlq_is_idempotent_on_replay(tmp_path):
    ev=[base_event('a',0,'x',1),base_event('b',700,'x',2),base_event('late',1,'x',9)]
    st={'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None}; cp={'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'}
    r=run_case(tmp_path,ev,st,cp); assert r.returncode==0
    dl=(tmp_path/'dlq.jsonl').read_text().splitlines()
    assert len(dl)==1
    # same durable state/checkpoint: rerun must not append a second DLQ copy
    r2=run_case(tmp_path,solution=True,reset=False); assert r2.returncode==0
    assert len((tmp_path/'dlq.jsonl').read_text().splitlines())==1
