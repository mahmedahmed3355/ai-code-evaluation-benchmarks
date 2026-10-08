import json, os, subprocess, sys, tempfile
from pathlib import Path
import torch
ROOT=Path(os.environ.get('TASK_ROOT','/app')); sys.path.insert(0,str(ROOT))
from app.reference import reference_state
CFG=json.load(open(ROOT/'data/config.json'))

def run(out,resume=None,stop=None,config=None):
    cmd=[sys.executable,'-m','app.run','--outdir',out]
    if resume: cmd += ['--resume',resume]
    if stop is not None: cmd += ['--stop-after',str(stop)]
    env={**os.environ,'PYTHONPATH':str(ROOT)}
    if config is None:
        subprocess.run(cmd,check=True,env=env)
    else:
        cfgpath=Path(out).parent/'config.json'; cfgpath.write_text(json.dumps(config))
        code=f'from app.trainer import train; import json; train(json.load(open({str(cfgpath)!r})),{str(out)!r})'
        subprocess.run([sys.executable,'-c',code],check=True,env=env)

def md(a,b): return max((a[k]-b[k]).abs().max().item() for k in a)

def test_reference_match():
    with tempfile.TemporaryDirectory() as d:
        run(d); got=torch.load(Path(d)/'final.pt',map_location='cpu',weights_only=False); ref,_,steps=reference_state(CFG['seed'],CFG)
        assert got['global_step']==steps==2 and md(ref,got['model'])<1e-7

def test_partial_accumulation_window():
    with tempfile.TemporaryDirectory() as d:
        cfg=dict(CFG); cfg['accumulation_steps']=4; cfg['total_optimizer_updates']=2
        run(d,config=cfg)
        got=torch.load(Path(d)/'final.pt',map_location='cpu',weights_only=False); ref,_,_=reference_state(CFG['seed'],cfg,2)
        assert md(ref,got['model'])<1e-7

def test_resume_equivalence():
    with tempfile.TemporaryDirectory() as d:
        cfg=dict(CFG); cfg['accumulation_steps']=4
        full=d+'/full'; first=d+'/first'; resumed=d+'/resumed'
        run(full,config=cfg); run(first,stop=1,config=cfg); run(resumed,resume=first+'/final.pt',config=cfg)
        a=torch.load(full+'/final.pt',map_location='cpu',weights_only=False); b=torch.load(resumed+'/final.pt',map_location='cpu',weights_only=False)
        assert a['global_step']==b['global_step']==2 and a['sample_cursor']==b['sample_cursor'] and md(a['model'],b['model'])<1e-7

def test_checkpoint_contract():
    with tempfile.TemporaryDirectory() as d:
        run(d,stop=1); c=torch.load(Path(d)/'checkpoint.pt',map_location='cpu',weights_only=False)
        assert set(c)=={'model','optimizer','global_step','sample_cursor'} and c['global_step']==1

def test_ddp_and_manual_gradient_sync_contract():
    s=(ROOT/'app/trainer.py').read_text()
    assert 'DistributedDataParallel' in s and 'no_sync' in s and 'all_reduce' in s

def test_data_preserved():
    ds=json.load(open(ROOT/'data/dataset.json')); assert len(ds['rank0'])==5 and len(ds['rank1'])==5

def test_no_reference_import():
    for p in (ROOT/'app').glob('*.py'):
        if p.name!='reference.py': assert 'reference_state' not in p.read_text()

def test_no_hardcoded_reference_weights():
    s=(ROOT/'app/trainer.py').read_text()
    assert 'reference_state' not in s and 'final.pt' in s

def test_stable_distributed_endpoint():
    s=(ROOT/'app/trainer.py').read_text()
    assert 'abs(hash(outdir))' not in s and 'FORGE_DDP_PORT' in s and 'socket.socket' in s
