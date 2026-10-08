import argparse
from .trainer import train

def main():
    p=argparse.ArgumentParser(); p.add_argument("--outdir",required=True); p.add_argument("--resume"); p.add_argument("--stop-after",type=int)
    a=p.parse_args(); train(outdir=a.outdir,resume=a.resume,stop_after=a.stop_after)

if __name__=="__main__": main()
