import json, torch
from .model import TinyNet

def reference_state(seed, cfg, updates=None):
    updates = updates or cfg["total_optimizer_updates"]
    ds=json.load(open(__import__('os').path.abspath(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','data','dataset.json'))))
    torch.manual_seed(seed); model=TinyNet(cfg["input_dim"],cfg["hidden_dim"],cfg["output_dim"])
    opt=torch.optim.SGD(model.parameters(),lr=cfg["learning_rate"])
    ordered=[]; i=0
    while True:
        added=False
        for r in ("rank0","rank1"):
            if i < len(ds[r]): ordered.append(ds[r][i]); added=True
        if not added: break
        i+=1
    pos=0
    for _ in range(updates):
        window=ordered[pos:pos+cfg["accumulation_steps"]*2]; pos+=len(window)
        if not window: break
        opt.zero_grad(set_to_none=True); total=len(window)
        for row in window:
            x=torch.tensor(row[0],dtype=torch.float32).unsqueeze(0); y=torch.tensor([row[1]])
            torch.nn.functional.cross_entropy(model(x),y,reduction="sum").div(total).backward()
        opt.step()
    return model.state_dict(),opt.state_dict(), min(updates, (len(ordered)+cfg["accumulation_steps"]*2-1)//(cfg["accumulation_steps"]*2))
