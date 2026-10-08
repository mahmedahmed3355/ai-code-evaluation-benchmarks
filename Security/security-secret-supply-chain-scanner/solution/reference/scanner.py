import argparse,json,re,base64,math,hashlib
from pathlib import Path
def ent(s):
    c={x:s.count(x) for x in set(s)}; n=len(s)
    return -sum((v/n)*math.log2(v/n) for v in c.values())
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--root",required=True); ap.add_argument("--config",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
    root=Path(a.root); cfg=json.loads(Path(a.config).read_text()); ignored=cfg.get("paths",[]); rules=set(cfg.get("rules",[])); linep=cfg.get("line_patterns",[])
    def ignpath(rel):
        import fnmatch
        return any(fnmatch.fnmatch(rel,x) for x in ignored) or rel==".git" or rel.startswith(".git/")
    rs=[]
    def add(rule,level,rel,line,col,msg):
        if rule in rules or any(x in msg for x in []): return
        for pat in linep:
            if pat in current: return
        key=f"{rel}:{line}:{col}:{rule}"
        fp=hashlib.sha256(key.encode()).hexdigest()[:16]
        rs.append({"ruleId":rule,"level":level,"message":{"text":msg},
          "locations":[{"physicalLocation":{"artifactLocation":{"uri":rel},"region":{"startLine":line,"startColumn":col}}}],
          "partialFingerprints":{"primaryLocationLineHash":fp}})
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.is_symlink(): continue
        rel=p.relative_to(root).as_posix()
        if ignpath(rel): continue
        try:
            if p.stat().st_size>2*1024*1024:
                f=p.open("r",encoding="utf-8",errors="ignore")
                lines=enumerate(f,1)
            else: lines=enumerate(p.read_text(encoding="utf-8").splitlines(),1)
            for ln,current in lines:
                if not isinstance(current,str): current=str(current)
                for m in re.finditer(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",current): add("SECRET001","error",rel,ln,m.start()+1,"AWS credential-like key")
                if "BEGIN PRIVATE KEY" in current or "BEGIN RSA PRIVATE KEY" in current: add("SECRET002","error",rel,ln,current.find("-----BEGIN")+1,"PEM private key")
                for m in re.finditer(r"\b(?:ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,})\b",current): add("SECRET003","error",rel,ln,m.start()+1,"GitHub token")
                for m in re.finditer(r"\b[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b",current):
                    try:
                        h=m.group().split(".")[0]; h+="="*((4-len(h)%4)%4); x=json.loads(base64.urlsafe_b64decode(h)); 
                        if "alg" in x and "typ" in x: add("SECRET004","error",rel,ln,m.start()+1,"JWT credential")
                    except Exception: pass
                for m in re.finditer(r"(?i)\b(PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY)\s*=\s*([^\s#]+)",current):
                    v=m.group(2)
                    if v.startswith("$") or v.lower() in {"changeme","example","placeholder","test","true","false"}: continue
                    add("SECRET005","error",rel,ln,m.start(2)+1,"credential assignment")
                for m in re.finditer(r"(?<![A-Za-z0-9])[A-Za-z0-9_!@#$%^&*+=-]{24,}(?![A-Za-z0-9])",current):
                    v=m.group()
                    if len(set(v))>=10 and ent(v)>=4.0 and not re.fullmatch(r"[0-9a-fA-F]{32,64}",v): add("SECRET006","warning",rel,ln,m.start()+1,"high-entropy token")
                if p.name=="Dockerfile":
                    m=re.match(r"\s*FROM\s+([^\s]+)",current,re.I)
                    if m and "@sha256:" not in m.group(1) and (":" not in m.group(1) or m.group(1).endswith(":latest")): add("DEP001","warning",rel,ln,1,"floating container base")
                if p.name in {"requirements.txt","requirements.in"} and current.strip() and not current.lstrip().startswith("#"):
                    if re.match(r"^[A-Za-z0-9_.-]+\s*(?:>=|~=|$)",current): add("DEP002","warning",rel,ln,1,"unpinned Python dependency")
        except (UnicodeDecodeError,OSError): continue
    rs.sort(key=lambda x:(x["locations"][0]["physicalLocation"]["artifactLocation"]["uri"],x["locations"][0]["physicalLocation"]["region"]["startLine"],x["locations"][0]["physicalLocation"]["region"].get("startColumn",0),x["ruleId"]))
    out={"version":"2.1.0","$schema":"https://json.schemastore.org/sarif-2.1.0.json","runs":[{"tool":{"driver":{"name":"forge-secret-scanner","rules":[]}},"results":rs}]}
    Path(a.out).write_text(json.dumps(out,sort_keys=True,indent=2))
if __name__=="__main__": main()
