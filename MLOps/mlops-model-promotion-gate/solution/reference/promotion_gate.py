import argparse,json,hashlib,re
from pathlib import Path
def ver(v):
    m=re.fullmatch(r"(\d+)\.(\d+)\.(\d+)",str(v))
    if not m: raise ValueError()
    return tuple(map(int,m.groups()))
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--candidate",required=True); ap.add_argument("--registry",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
    c=json.load(open(a.candidate)); r=json.load(open(a.registry)); reasons=[]
    try:
        name=c["model_name"]; version=c["version"]; stage=c["stage"]; art=c["artifact"]; model=Path(art["path"])
        if name!=r["model_name"]: reasons.append("model_name_mismatch")
        if stage not in ("dev","staging"): reasons.append("invalid_candidate_stage")
        cur=r.get(stage,{}).get("version","0.0.0")
        if ver(version)<=ver(cur): reasons.append("version_not_greater")
        if not model.exists(): reasons.append("artifact_missing")
        else:
            got=hashlib.sha256(model.read_bytes()).hexdigest()
            if got!=art["sha256"]: reasons.append("artifact_checksum_mismatch")
        d=c["training"]["dataset_id"]; dv=c["training"]["dataset_version"]; ds=r["allowed_datasets"][d]
        if dv in ds.get("revoked",[]): reasons.append("dataset_revoked")
        if ver(dv)<ver(ds["min_version"]): reasons.append("dataset_too_old")
        if not c["training"].get("code_commit"): reasons.append("missing_code_commit")
        if c["evaluation"]["samples"]<r["policy"]["min_samples"]: reasons.append("insufficient_samples")
        metrics=c["evaluation"]["metrics"]; pol=r["policy"]["required_metrics"]
        for m,rule in pol.items():
            if m not in metrics: reasons.append(f"missing_metric:{m}"); continue
            x=metrics[m]
            if rule["higher_is_better"]:
                if x<rule["threshold"]: reasons.append(f"below_threshold:{m}")
            else:
                if x>rule["threshold"]: reasons.append(f"above_threshold:{m}")
            base=r["production"]["metrics"].get(m)
            if base is not None:
                if rule["higher_is_better"] and x<base-rule["max_regression"]: reasons.append(f"regression:{m}")
                if not rule["higher_is_better"] and x>base+rule["max_regression"]: reasons.append(f"regression:{m}")
        if stage=="staging":
            if not c.get("approval",{}).get("approved",False): reasons.append("approval_required")
            if c.get("evaluation",{}).get("reference",{}).get("dataset_version") and ver(c["evaluation"]["reference"]["dataset_version"])<ver(r["allowed_datasets"][d]["min_version"]): reasons.append("stale_evaluation")
        else: reasons.append("direct_production_forbidden")
    except Exception: reasons.append("malformed_candidate")
    reasons=sorted(set(reasons)); decision="promote" if not reasons else "reject"
    out={"decision":decision,"target_stage":"production","model_name":c.get("model_name"),"version":c.get("version"),"reasons":reasons}
    Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2))
if __name__=="__main__": main()
