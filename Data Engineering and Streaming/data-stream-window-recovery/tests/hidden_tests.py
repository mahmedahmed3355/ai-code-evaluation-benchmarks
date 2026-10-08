import json, shutil, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
ROOT=Path('/app'); BASE=ROOT/'environment/data'
W0=lambda day: str(int(datetime(2026,day,1,tzinfo=timezone.utc).timestamp())//300*300)
W0F=W0(2); W1F=str(int(datetime(2026,2,1,tzinfo=timezone.utc).timestamp()+300)//300*300)
def ev(i,s,k='k',v=1):
 t=datetime(2026,2,1,tzinfo=timezone.utc)+timedelta(seconds=s); return {'event_id':i,'event_time':t.isoformat().replace('+00:00','Z'),'key':k,'value':v}
def run(events, state=None, cp=None, cfg=None):
 d=tempfile.mkdtemp(prefix='streamtest-')
 p=Path(d)
 for n in ['config.json']: shutil.copy2(BASE/n,p/n)
 (p/'events.jsonl').write_text('\n'.join(json.dumps(x) for x in events)+'\n')
 (p/'state.json').write_text(json.dumps(state or {'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None}))
 (p/'checkpoint.json').write_text(json.dumps(cp or {'committed_offset':-1,'generation':0,'last_commit_kind':'state_then_offset'}))
 (p/'output.json').write_text('[]'); (p/'dlq.jsonl').write_text('')
 c=[sys.executable,'-m','solution.streaming.cli','--events',str(p/'events.jsonl'),'--state',str(p/'state.json'),'--checkpoint',str(p/'checkpoint.json'),'--output',str(p/'output.json'),'--dlq',str(p/'dlq.jsonl'),'--config',str(p/'config.json')]
 r=subprocess.run(c,cwd='/app',env={'PYTHONPATH':'/app'},capture_output=True,text=True)
 return r,p

def test_hidden_out_of_order_01():
 r,p=run([ev('a',400,v=4),ev('b',50,v=5),ev('c',620,v=6)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['sum']==5

def test_hidden_out_of_order_02():
 r,p=run([ev('a',620,v=1),ev('b',300,v=2),ev('c',299,v=3)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['sum']==3 and s['windows'][W1F]['sum']==2

def test_hidden_duplicate_mutated_payload():
 a=ev('same',10,v=7); b=ev('same',10,v=700); r,p=run([a,b]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==7

def test_hidden_duplicate_different_key():
 r,p=run([ev('same',10,'a',7),ev('same',10,'evil',700)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['by_key']=={'a':7.0}

def test_hidden_boundary_120():
 r,p=run([ev('a',0,v=1),ev('b',420,v=2),ev('c',300,v=9)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W1F]['sum']==11

def test_hidden_boundary_121_is_still_window_if_not_finalized():
 r,p=run([ev('a',0,v=1),ev('b',421,v=2),ev('c',300,v=9)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W1F]['sum']==11

def test_hidden_finalization_never_reopens():
 r,p=run([ev('a',0,v=1),ev('b',1000,v=2),ev('c',10,v=99)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['sum']==1

def test_hidden_checkpoint_zero():
 st={'seen_event_ids':[],'windows':{},'finalized_windows':[],'max_event_ts':None}; cp={'committed_offset':-1,'generation':9,'last_commit_kind':'state_then_offset'}; r,p=run([ev('a',1,v=3)],st,cp); assert r.returncode==0

def test_hidden_checkpoint_midstream():
 st={'seen_event_ids':['a','b'],'windows':{W0F:{'count':2,'sum':3,'by_key':{'k':3}}},'finalized_windows':[],'max_event_ts':20.0}; cp={'committed_offset':1,'generation':4,'last_commit_kind':'state_then_offset'}; r,p=run([ev('a',10,v=1),ev('b',20,v=2),ev('c',30,v=5)],st,cp); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==8

def test_hidden_large_1000():
 es=[ev(str(i),i%900,k=str(i%9),v=(i%13)+.25) for i in range(1000)]; r,p=run(es); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert sum(w['count'] for w in s['windows'].values())==900

def test_hidden_many_duplicates():
 es=[]
 for i in range(100):
  e=ev(str(i),i,v=1); es += [e,dict(e),dict(e)]
 r,p=run(es); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert sum(w['count'] for w in s['windows'].values())==100

def test_hidden_empty_input():
 r,p=run([]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['seen_event_ids']==[]

def test_hidden_negative_value():
 r,p=run([ev('a',1,v=-4),ev('b',2,v=9)]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==5

def test_hidden_zero_value():
 r,p=run([ev('a',1,v=0),ev('b',2,v=0)]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==0

def test_hidden_key_cardinality():
 es=[ev(str(i),i,k=f'k{i}',v=1) for i in range(50)]; r,p=run(es); assert r.returncode==0; assert len(json.loads((p/'state.json').read_text())['windows'][W0F]['by_key'])==50

def test_hidden_late_event_id_is_marked_seen():
 r,p=run([ev('a',0),ev('b',1000),ev('late',1,v=99)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert 'late' in s['seen_event_ids']

def test_hidden_late_event_not_in_output():
 r,p=run([ev('a',0,v=1),ev('b',1000,v=2),ev('late',1,v=99)]); assert r.returncode==0; out=json.loads((p/'output.json').read_text()); assert out[0]['sum']==1

def test_hidden_output_sorted():
 r,p=run([ev('a',1000),ev('b',10),ev('c',600)]); assert r.returncode==0; out=json.loads((p/'output.json').read_text()); assert [int(x['window_start']) for x in out]==sorted(int(x['window_start']) for x in out)

def test_hidden_by_key_sorted():
 r,p=run([ev('a',1,'z',1),ev('b',2,'a',2),ev('c',700,'q',0)]); assert r.returncode==0; out=json.loads((p/'output.json').read_text()); assert list(out[0]['by_key'])==['a','z']

def test_hidden_config_lateness_change():
 r,p=run([ev('a',0),ev('b',500),ev('late',100,v=9)],cfg={'window_seconds':300,'allowed_lateness_seconds':60,'delivery_semantics':'at_least_once','aggregation':'sum_and_count','dedupe_key':'event_id'}); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['sum']==1

def test_hidden_large_values():
 r,p=run([ev('a',1,v=1e12),ev('b',2,v=2e12)]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==3e12

def test_hidden_decimal_precision():
 r,p=run([ev('a',1,v=.1),ev('b',2,v=.2),ev('c',3,v=.3)]); assert r.returncode==0; assert abs(json.loads((p/'state.json').read_text())['windows'][W0F]['sum']-.6)<1e-9

def test_hidden_same_timestamp():
 r,p=run([ev('a',100,v=1),ev('b',100,v=2)]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['count']==2

def test_hidden_event_at_window_end():
 r,p=run([ev('a',299,v=1),ev('b',300,v=2)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][W0F]['sum']==1 and s['windows'][W1F]['sum']==2

def test_hidden_negative_window_timestamp():
 r,p=run([ev('a',-1,v=2),ev('b',10,v=3)]); assert r.returncode==0; s=json.loads((p/'state.json').read_text()); assert s['windows'][str(int(datetime(2026,2,1,tzinfo=timezone.utc).timestamp()-300)//300*300)]['sum']==2

def test_hidden_recovery_generation_increments():
 r,p=run([ev('a',1),ev('b',2)]); assert r.returncode==0; assert json.loads((p/'checkpoint.json').read_text())['generation']==2

def test_hidden_checkpoint_rejects_future_offset():
 r,p=run([ev('a',1)],cp={'committed_offset':99,'generation':1,'last_commit_kind':'state_then_offset'}); assert r.returncode!=0

def test_hidden_checkpoint_rejects_wrong_order():
 r,p=run([ev('a',1)],cp={'committed_offset':-1,'generation':1,'last_commit_kind':'offset_then_state'}); assert r.returncode!=0

def test_hidden_malformed_event_fails_closed():
 r,p=run([{'event_id':'x','event_time':'2026-02-01T00:00:00Z','key':'k'}]); assert r.returncode!=0

def test_hidden_invalid_timestamp_fails_closed():
 r,p=run([{'event_id':'x','event_time':'not-a-time','key':'k','value':1}]); assert r.returncode!=0

def test_hidden_missing_state_fields_recovered():
 r,p=run([ev('a',1)],state={}); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['count']==1

def test_hidden_duplicate_after_checkpoint():
 st={'seen_event_ids':['a'],'windows':{W0F:{'count':1,'sum':4,'by_key':{'k':4}}},'finalized_windows':[],'max_event_ts':1.0}; cp={'committed_offset':0,'generation':1,'last_commit_kind':'state_then_offset'}; r,p=run([ev('a',1,v=400),ev('b',2,v=3)],st,cp); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==7

def test_hidden_finalized_state_preserved_on_replay():
 st={'seen_event_ids':['a'],'windows':{W0F:{'count':1,'sum':1,'by_key':{'k':1}}},'finalized_windows':[W0F],'max_event_ts':1000.0}; cp={'committed_offset':0,'generation':1,'last_commit_kind':'state_then_offset'}; r,p=run([ev('a',1,v=99),ev('late',2,v=88)],st,cp); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['windows'][W0F]['sum']==1

def test_hidden_dlq_contains_reason():
 r,p=run([ev('a',0),ev('b',1000),ev('late',1)]); assert r.returncode==0; x=json.loads((p/'dlq.jsonl').read_text().splitlines()[0]); assert x['reason']=='late_after_finalization'

def test_hidden_dlq_offset_recorded():
 r,p=run([ev('a',0),ev('b',1000),ev('late',1)]); assert r.returncode==0; x=json.loads((p/'dlq.jsonl').read_text().splitlines()[0]); assert x['offset']==2

def test_hidden_output_has_counts():
 r,p=run([ev('a',0),ev('b',1000)]); assert r.returncode==0; assert 'count' in json.loads((p/'output.json').read_text())[0]

def test_hidden_output_has_by_key():
 r,p=run([ev('a',0),ev('future',700)]); assert r.returncode==0; assert 'by_key' in json.loads((p/'output.json').read_text())[0]

def test_hidden_state_seen_sorted():
 r,p=run([ev('z',1),ev('a',2),ev('m',3)]); assert r.returncode==0; assert json.loads((p/'state.json').read_text())['seen_event_ids']==['a','m','z']

def test_hidden_finalized_sorted():
 r,p=run([ev('a',0),ev('b',1000),ev('c',2000)]); assert r.returncode==0; f=json.loads((p/'state.json').read_text())['finalized_windows']; assert f==sorted(f,key=int)

def test_hidden_idempotent_three_runs():
 r,p=run([ev('a',0),ev('b',1000),ev('late',1)]); assert r.returncode==0; before=(p/'dlq.jsonl').read_text();
 for _ in range(2):
  c=[sys.executable,'-m','solution.streaming.cli','--events',str(p/'events.jsonl'),'--state',str(p/'state.json'),'--checkpoint',str(p/'checkpoint.json'),'--output',str(p/'output.json'),'--dlq',str(p/'dlq.jsonl'),'--config',str(p/'config.json')]; rr=subprocess.run(c,cwd='/app',env={'PYTHONPATH':'/app'}); assert rr.returncode==0
 assert (p/'dlq.jsonl').read_text()==before
