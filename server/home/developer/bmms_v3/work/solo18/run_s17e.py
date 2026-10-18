"""Remote serial precision experiment, preserving fail-first semantics and all evidence."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,time
r=Path('/home/developer/bmms_v3');out=r/'solo17_data/diagnostic_s17e'
out.mkdir(exist_ok=False)
for _ in range(80):
    log=(r/'variants/s17e/build.log').read_text()
    if all('Built target '+x in log for x in ['bench','bench_cases','bench_multi']):break
    if 'error:' in log:raise SystemExit('compile failed, see build.log')
    time.sleep(10)
else:raise SystemExit('compile not complete')
lock=(r/'solo17_data/.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants/s17e/build/bench_cases';src=r/'variants/s17e/kernel.asc'
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
summary=[]
for name,manifest in [('fail_8',r/'work/solo18/fail_8.txt'),('medium_256',r/'solo17_data/medium_cases.txt'),('split_160',r/'solo14_data/split16_cases.txt')]:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(name+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    passed=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=name,passed=passed,observed=len(rows),returncode=p.returncode)
    summary.append(item);print(json.dumps(item),flush=True)
    (out/'summary.json').write_text(json.dumps(dict(suites=summary,hashes=hashes),indent=2))
    if not passed:print(p.stdout[-3000:]+p.stderr[-2000:],flush=True);raise SystemExit(1)
assert hashes=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
fcntl.flock(lock,fcntl.LOCK_UN)
# Full historical + medium protocol, including out-of-official-range robustness suite.
p=subprocess.run(['python3',str(r/'work/solo17/validate.py'),'s17e'])
raise SystemExit(p.returncode)
