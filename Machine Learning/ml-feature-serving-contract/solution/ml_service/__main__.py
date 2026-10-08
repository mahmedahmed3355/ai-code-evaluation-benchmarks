import json,sys
from .inference import predict_file
if len(sys.argv)!=2:
    print("ERROR: usage: python -m ml_service INPUT.csv",file=sys.stderr); sys.exit(2)
try:
    p=predict_file(sys.argv[1])
    print(json.dumps({"predictions":[float(x) for x in p]},separators=(",",":")))
except Exception as e:
    print(f"ERROR: {e}",file=sys.stderr); sys.exit(1)
