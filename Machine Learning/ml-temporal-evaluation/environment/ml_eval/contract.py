import json
def load_contract(schema_path, artifact_path):
 with open(schema_path) as f: s=json.load(f)
 with open(artifact_path) as f: a=json.load(f)
 return s,a
