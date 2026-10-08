import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENV=ROOT/"environment"
SERVICE=ENV/"systemd/forge-worker.service"
DROP=ENV/"systemd/forge-worker.service.d/10-migration.conf"

def run(cmd): return subprocess.run(cmd,text=True,capture_output=True)
def assert_true(name,cond):
    print(f"{name}: {'PASS' if cond else 'FAIL'}")
    if not cond: raise AssertionError(name)
def last(key,lines):
    vals=[x.split('=',1)[1] for x in lines if x.startswith(key+'=')]
    return vals[-1] if vals else None

def structural():
    lines=SERVICE.read_text().splitlines(); drop=DROP.read_text(); text='\n'.join(lines)+'\n'+drop
    checks={
      'network-order': 'After=network-online.target' in text and 'Wants=network-online.target' in text,
      'environment-file': 'EnvironmentFile=/etc/forge/worker.env' in text,
      'preflight': '--validate-config' in text,
      'command': '/usr/local/bin/forge-worker --serve' in text,
      'user': last('User',lines)=='forge', 'group': last('Group',lines)=='forge',
      'memory': last('MemoryMax',lines)=='512M', 'nice': last('Nice',lines)=='5',
      'nnp': last('NoNewPrivileges',lines)=='yes', 'restart': last('Restart',lines)=='on-failure',
      'restart-sec': last('RestartSec',lines)=='3', 'burst': last('StartLimitBurst',lines)=='5',
      'interval': last('StartLimitIntervalSec',lines)=='60',
      'readiness': 'READINESS_AFTER_START=1' in drop,
      'clean-stop': 'CLEAN_STOP_IS_SUCCESS=1' in drop,
      'failure-recovery': 'TRANSIENT_FAILURE_RESTART=1' in drop,
      'no-shell-wrapper': '/bin/sh' not in SERVICE.read_text(),
      'no-bypass': all(x not in text.lower() for x in ['/bin/true','validation=pass','execstart=/bin/false'])
    }
    for k,v in checks.items(): assert_true(k,v)

def restore_baseline():
    SERVICE.write_text("""[Unit]
Description=Forge Worker
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
ExecStart=/bin/sh -c '/usr/local/bin/forge-worker --serve'
Restart=no
MemoryMax=1024M
Nice=0
NoNewPrivileges=no
EnvironmentFile=/etc/forge/old-worker.env
ExecStartPre=/usr/local/bin/forge-worker --validate-config
""")
    DROP.write_text("""[Service]
Environment=\"WORKER_CONFIG=/etc/forge/worker.yaml\"
Environment=\"WORKER_USER=forge\"
Environment=\"WORKER_MEMORY_MB=64\"
""")

def main():
    restore_baseline()
    baseline=run([sys.executable,str(ENV/'validate.sh')])
    assert_true('baseline-fails',baseline.returncode!=0)
    oracle=run([str(ROOT/'solution/solve.sh')])
    assert_true('oracle-pass',oracle.returncode==0 and 'VALIDATION=PASS' in oracle.stdout)
    structural()
    hidden=run([sys.executable,str(Path(__file__).with_name('hidden_tests.py'))])
    assert_true('hidden-tests',hidden.returncode==0 and 'HIDDEN_TESTS=PASS' in hidden.stdout)
    verifier=run([sys.executable,str(Path(__file__).with_name('verify.py'))])
    assert_true('independent-verifier',verifier.returncode==0 and 'VERIFIER=PASS' in verifier.stdout)
    print('TESTS=PASS')
if __name__=='__main__':
    try: main()
    except Exception as e: print('TESTS=FAIL',e); sys.exit(1)
