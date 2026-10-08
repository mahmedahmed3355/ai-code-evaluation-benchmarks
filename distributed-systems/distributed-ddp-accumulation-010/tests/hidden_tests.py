import json, os, subprocess, sys, tempfile
from pathlib import Path
import torch
ROOT=Path(os.environ.get('TASK_ROOT','/app')); sys.path.insert(0,str(ROOT))
from app.reference import reference_state

def test_hidden_alternate_config():
    base=json.load(open(ROOT/'data/config.json'))
    cfg={**base,'seed':29,'learning_rate':0.017,'accumulation_steps':2,'total_optimizer_updates':3}
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'cfg.json'; p.write_text(json.dumps(cfg))
        env={**os.environ,'PYTHONPATH':str(ROOT)}
        code=f'from app.trainer import train; import json; train(json.load(open({str(p)!r})),{str(Path(d)/"run")!r})'
        subprocess.run([sys.executable,'-c',code],env=env,check=True)
        got=torch.load(Path(d)/'run/final.pt',map_location='cpu',weights_only=False)
        ref,_,_=reference_state(cfg['seed'],cfg,updates=3)
        assert max((ref[k]-got['model'][k]).abs().max().item() for k in ref)<1e-7

def test_hidden_uneven_rank_shards():
    dataset=json.load(open(ROOT/'data/dataset.json'))
    original=(ROOT/'data/dataset.json').read_text()
    try:
        dataset['rank1']=dataset['rank1'][:4]
        (ROOT/'data/dataset.json').write_text(json.dumps(dataset))
        cfg=json.load(open(ROOT/'data/config.json')); cfg['accumulation_steps']=4; cfg['total_optimizer_updates']=2
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'cfg.json'; p.write_text(json.dumps(cfg)); env={**os.environ,'PYTHONPATH':str(ROOT)}
            code=f'from app.trainer import train; import json; train(json.load(open({str(p)!r})),{str(Path(d)/"run")!r})'
            subprocess.run([sys.executable,'-c',code],env=env,check=True)
            got=torch.load(Path(d)/'run/final.pt',map_location='cpu',weights_only=False)
            ref,_,steps=reference_state(cfg['seed'],cfg,updates=2)
            assert got['global_step']==steps and max((ref[k]-got['model'][k]).abs().max().item() for k in ref)<1e-7
    finally:
        (ROOT/'data/dataset.json').write_text(original)

def test_hidden_does_not_disable_ddp():
    s=(ROOT/'app/trainer.py').read_text()
    assert 'DistributedDataParallel' in s and 'dist.init_process_group' in s and 'all_reduce' in s
