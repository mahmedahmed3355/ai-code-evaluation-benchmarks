import hashlib
import numpy as np

def assign_groups(groups, seed, train_fraction, validation_fraction):
    uniq=sorted(set(int(x) for x in groups))
    def key(g): return hashlib.sha256(f"{seed}:{g}".encode()).hexdigest()
    ordered=sorted(uniq,key=key); n=len(ordered)
    a=int(n*train_fraction); b=int(n*(train_fraction+validation_fraction))
    if a<=0 or b<=a or b>=n: raise ValueError("invalid split fractions")
    tr=set(ordered[:a]); va=set(ordered[a:b]); ho=set(ordered[b:])
    out=np.array(['train' if int(g) in tr else 'validation' if int(g) in va else 'holdout' for g in groups])
    return out

def fingerprint(rows, assignment):
    h=hashlib.sha256()
    for r,a in sorted(zip(rows,assignment),key=lambda z:(int(z[0][0]),int(z[0][1]))): h.update(f"{int(r[0])},{int(r[1])},{a};".encode())
    return h.hexdigest()
