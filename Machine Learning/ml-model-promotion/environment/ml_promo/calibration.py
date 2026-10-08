import numpy as np
from .model import sigmoid,loss
def fit_temperature(logits,y,grid):
    best=None
    for t in grid:
        if t<=0: continue
        l=loss(y,sigmoid(logits/float(t)))
        if best is None or l<best[0] or (l==best[0] and t<best[1]): best=(l,float(t))
    if best is None: raise ValueError('no valid temperature')
    return best[1]
