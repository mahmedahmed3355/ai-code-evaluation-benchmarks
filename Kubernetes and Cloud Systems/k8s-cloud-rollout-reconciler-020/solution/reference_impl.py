
import argparse,json,sys
def bad(msg):
    return {"action":"reject","pod":None,"node":None,"reason":"invalid_input",
            "desired_revision":None,"available_replicas":0,"total_replicas":0,"old_replicas":0,"new_replicas":0}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--spec",required=True); ap.add_argument("--state",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args()
    try:
        s=json.load(open(a.spec)); c=json.load(open(a.state))
        w=s["workload"]; pt=s["pod_template"]; pol=s.get("policy",{})
        nodes=c["nodes"]; pods=c["pods"]
        for k in ("name","replicas","max_surge","max_unavailable","revision"): assert k in w
        if any(not isinstance(w[k],int) or w[k]<0 for k in ("replicas","max_surge","max_unavailable")): raise ValueError()
        req=pt["requests"]; assert isinstance(req,dict)
        cpu,mem=req["cpu_m"],req["memory_mib"]
        assert isinstance(cpu,int) and cpu>=0 and isinstance(mem,int) and mem>=0
        names=set()
        nd={}
        for n in nodes:
            assert n["name"] not in names; names.add(n["name"])
            assert n["name"] and "allocatable" in n and "used" in n
            for x in ("cpu_m","memory_mib"):
                assert isinstance(n["allocatable"][x],int) and n["allocatable"][x]>=0
                assert isinstance(n["used"][x],int) and n["used"][x]>=0
            nd[n["name"]]=n
        podnames=set()
        for p in pods:
            assert p["name"] not in podnames; podnames.add(p["name"])
            if p.get("workload")==w["name"]: assert p["node"] in nd
        topo=s.get("topology")
        if topo:
            tk=topo["key"]
            for n in nodes: assert tk in n
        desired=w["revision"]; desired_n=w["replicas"]
        def available(p):
            return (p.get("ready") is True and not p.get("terminating",False)
                    and nd[p["node"]].get("ready") is True
                    and p.get("ready_for_seconds",0)>=w.get("min_ready_seconds",0))
        wp=[p for p in pods if p.get("workload")==w["name"]]
        new=[p for p in wp if p.get("revision")==desired]
        old=[p for p in wp if p.get("revision")!=desired]
        av=sum(available(p) for p in wp)
        total=sum(not p.get("terminating",False) for p in wp)+sum(p.get("terminating",False) for p in wp)
        # total is intentionally all existing pods, including terminating
        total=len(wp); newn=len(new); oldn=len(old)
        base={"desired_revision":desired,"available_replicas":av,"total_replicas":total,
              "old_replicas":oldn,"new_replicas":newn}
        if newn==desired_n and oldn==0:
            out={"action":"noop","pod":None,"node":None,"reason":"rollout_complete",**base}
        else:
            surge=w["max_surge"]; floor=max(0,desired_n-w["max_unavailable"])
            feasible=[]
            for n in nodes:
                if not n.get("ready",False): continue
                remcpu=n["allocatable"]["cpu_m"]-n["used"]["cpu_m"]
                remmem=n["allocatable"]["memory_mib"]-n["used"]["memory_mib"]
                if remcpu<cpu or remmem<mem: continue
                if topo:
                    counts={}
                    domains={x[topo["key"]] for x in nodes if x.get("ready",False)}
                    for d in domains: counts[d]=0
                    for p in wp:
                        if not p.get("terminating",False): counts[nd[p["node"]][topo["key"]]]=counts.get(nd[p["node"]][topo["key"]],0)+1
                    d= n[topo["key"]]; counts[d]=counts.get(d,0)+1
                    if max(counts.values())-min(counts.values())>topo["max_skew"]: continue
                    skew=max(counts.values())-min(counts.values())
                else: skew=0
                feasible.append((skew,-remcpu,n["name"]))
            if total < desired_n+surge and feasible:
                _,_,nn=min(feasible)
                ords=[]
                prefix=f"{w['name']}-{desired}-"
                for p in wp:
                    if p["revision"]==desired and p["name"].startswith(prefix):
                        try: ords.append(int(p["name"][len(prefix):]))
                        except: pass
                ordinal=0
                while ordinal in ords: ordinal+=1
                pod=f"{prefix}{ordinal}"
                out={"action":"create","pod":pod,"node":nn,"reason":"surge_capacity_available",**base}
            else:
                safe=[]
                for p in old:
                    if p.get("terminating",False) or not available(p): continue
                    after=av-1
                    if after<floor: continue
                    if "pdb" in s and after<s["pdb"]["min_available"]: continue
                    if newn<desired_n: continue
                    safe.append((-p.get("age_seconds",0),p["name"],p))
                if safe:
                    p=min(safe)[2]
                    out={"action":"delete","pod":p["name"],"node":p["node"],"reason":"old_pod_safe_to_remove",**base}
                elif (newn==0 and oldn>0 and pol.get("allow_rollback",False)
                      and pol.get("rollback_revision") is not None and w.get("rollback_revision") in {p.get("revision") for p in old}
                      and total >= desired_n+surge and not feasible):
                    rb=w["rollback_revision"]
                    out={"action":"rollback","pod":None,"node":None,"reason":"rollback_due_to_unschedulable_revision",
                         **{**base,"desired_revision":rb}}
                elif not feasible:
                    out={"action":"wait","pod":None,"node":None,"reason":"waiting_for_capacity",**base}
                else:
                    out={"action":"wait","pod":None,"node":None,"reason":"waiting_for_readiness",**base}
        with open(a.out,"w") as f: json.dump(out,f,sort_keys=True)
    except Exception:
        out=bad("invalid")
        with open(a.out,"w") as f: json.dump(out,f,sort_keys=True)
if __name__=="__main__": main()
