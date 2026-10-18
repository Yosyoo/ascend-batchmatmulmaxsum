from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';out=d/'unaligned_23i';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants/s23i/build/bench_unaligned';source=r/'variants/s23i/kernel.asc'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='be327461b89963ee31f33989983c41522b40e0d4e056f9d470fae0f45931b8df'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,source]}
fixtures=json.loads((d/'dot_once_input_sha256.json').read_text())
def check():
    for name,sha in fixtures.items():assert hashlib.sha256((d/name).read_bytes()).hexdigest()==sha
check();summary=[]
for a,b in [(2,0),(0,2),(2,2)]:
    p=subprocess.run([str(exe),str(d/'dot_once_cases.txt'),str(a),str(b)],capture_output=True,text=True,timeout=600)
    (out/f'offset_{a}_{b}.log').write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==576 and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(offsetA=a,offsetB=b,passed=good,observed=len(rows),expected=576,hashes=hashes)
    summary.append(item);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(item),flush=True)
    if not good:raise SystemExit(1)
check();assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,source]}
(out/'integrity.json').write_text(json.dumps(dict(all_fixture_hashes_unchanged=True,metadata_sha256=hashlib.sha256((d/'dot_once_input_sha256.json').read_bytes()).hexdigest()),indent=2)+'\n')
print('PASS actual2-byte unaligned inputs,1728cases,3identical executions each',flush=True)
