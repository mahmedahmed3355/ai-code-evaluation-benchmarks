import argparse, json
from .processor import process
p=argparse.ArgumentParser()
p.add_argument('--events',required=True); p.add_argument('--state',required=True); p.add_argument('--checkpoint',required=True); p.add_argument('--output',required=True); p.add_argument('--dlq',required=True); p.add_argument('--config',required=True)
a=p.parse_args(); process(a.events,a.state,a.checkpoint,a.output,a.dlq,a.config)
