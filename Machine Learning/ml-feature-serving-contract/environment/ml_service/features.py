import csv,numpy as np
def iter_chunks(path,schema,chunk_size=64,require_target=False):
    with open(path,newline="",encoding="utf-8-sig") as f:
        r=csv.reader(f); cols=next(r); 
        for row in r:
            if not row: continue
            # BUG: incoming column order is treated as model order.
            vals=[float(v) if v.strip() else 0.0 for v in row[:len(schema["features"])]]
            y=int(row[-1]) if require_target else None
            yield np.asarray([vals],float),(np.asarray([y],int) if require_target else None)
