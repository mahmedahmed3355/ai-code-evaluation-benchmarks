import json, os, random, socket, torch
import torch.distributed as dist
import torch.multiprocessing as mp
from .model import TinyNet

def _seed(seed): random.seed(seed); torch.manual_seed(seed)
def _data_path(name): return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', name))
def _load_cfg(path=None):
    with open(path or _data_path('config.json')) as f: return json.load(f)
def _load_data():
    with open(_data_path('dataset.json')) as f: return json.load(f)

def _run_rank(rank, cfg, outdir, resume=None, stop_after=None):
    _seed(cfg['seed'])
    os.environ['MASTER_ADDR']='127.0.0.1'; os.environ['MASTER_PORT']=os.environ.get('FORGE_DDP_PORT','29517')
    dist.init_process_group('gloo', rank=rank, world_size=cfg['world_size'])
    model=TinyNet(cfg['input_dim'],cfg['hidden_dim'],cfg['output_dim'])
    ddp=torch.nn.parallel.DistributedDataParallel(model)
    opt=torch.optim.SGD(ddp.parameters(),lr=cfg['learning_rate'])
    global_step=0; sample_cursor=0
    if resume:
        ck=torch.load(resume,map_location='cpu',weights_only=False)
        ddp.load_state_dict(ck['model']); opt.load_state_dict(ck['optimizer'])
        global_step=ck['global_step']; sample_cursor=ck['sample_cursor']
    data=_load_data()[f'rank{rank}']
    target=stop_after or cfg['total_optimizer_updates']
    while global_step < target:
        local_rows=data[sample_cursor:sample_cursor+cfg['accumulation_steps']]
        count=torch.tensor([len(local_rows)],dtype=torch.int64)
        dist.all_reduce(count,op=dist.ReduceOp.SUM)
        total_samples=int(count.item())
        if total_samples == 0: break
        opt.zero_grad(set_to_none=True)
        with ddp.no_sync():
            for row in local_rows:
                x=torch.tensor(row[0],dtype=torch.float32).unsqueeze(0); y=torch.tensor([row[1]])
                (torch.nn.functional.cross_entropy(ddp(x),y,reduction='sum')/total_samples).backward()
        for param in ddp.parameters():
            if param.grad is None:
                param.grad=torch.zeros_like(param)
            dist.all_reduce(param.grad,op=dist.ReduceOp.SUM)
        opt.step(); global_step+=1; sample_cursor+=cfg['accumulation_steps']
        if global_step==cfg['checkpoint_after_updates'] and outdir:
            if rank==0:
                os.makedirs(outdir,exist_ok=True); torch.save({'model':ddp.module.state_dict(),'optimizer':opt.state_dict(),'global_step':global_step,'sample_cursor':sample_cursor},outdir+'/checkpoint.pt')
            dist.barrier()

    if rank==0:
        os.makedirs(outdir,exist_ok=True); torch.save({'model':ddp.module.state_dict(),'optimizer':opt.state_dict(),'global_step':global_step,'sample_cursor':sample_cursor},outdir+'/final.pt')
    dist.destroy_process_group()

def train(config=None,outdir='/tmp/ddp-run',resume=None,stop_after=None):
    cfg=config or _load_cfg(); sock=socket.socket(); sock.bind(('127.0.0.1',0)); os.environ['FORGE_DDP_PORT']=str(sock.getsockname()[1]); sock.close(); mp.spawn(_run_rank,args=(cfg,outdir,resume,stop_after),nprocs=cfg['world_size'],join=True)
