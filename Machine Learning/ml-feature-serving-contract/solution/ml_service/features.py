import csv, numpy as np
def _num(v):
    if v.strip().lower() in {"","na","n/a","null","none","nan"}: return np.nan
    x=float(v)
    if not np.isfinite(x): raise ValueError("non-finite feature")
    return x
def iter_chunks(path, schema, chunk_size=64, require_target=False):
    with open(path,newline="",encoding="utf-8-sig") as f:
        r=csv.reader(f); cols=[c.strip() for c in next(r)]
        if len(cols)!=len(set(cols)): raise ValueError("duplicate columns")
        for c in schema["features"]:
            if c not in cols: raise ValueError("missing feature")
        allowed=set(schema["features"])|{schema["target"]}
        if any(c not in allowed for c in cols): raise ValueError("unexpected feature")
        if require_target and schema["target"] not in cols: raise ValueError("missing target")
        buf=[]; ys=[]
        for row in r:
            if not row or not any(x.strip() for x in row): continue
            if len(row)!=len(cols): raise ValueError("malformed row")
            d=dict(zip(cols,row))
            buf.append([_num(d[c]) for c in schema["features"]])
            if require_target: ys.append(int(d[schema["target"]]))
            if len(buf)==chunk_size:
                yield np.asarray(buf,float),(np.asarray(ys,int) if require_target else None); buf=[]; ys=[]
        if buf: yield np.asarray(buf,float),(np.asarray(ys,int) if require_target else None)
