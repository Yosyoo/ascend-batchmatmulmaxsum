from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s20c'
out=d/'diagnostic_20c';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='e3b429c07ee8a2d133151a4ee6c09f1621d5d82dc207560da4a1f7152c38ee8d'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]};items=[]
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt',d/'manual_cases18.txt',d/'medium_cases.txt',r/'solo14_data/split16_cases.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),expected=len(manifest.read_text().splitlines()),hashes=hashes);items.append(item)
    (out/'summary.json').write_text(json.dumps(items,indent=2));print(json.dumps(item),flush=True)
    if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
fcntl.flock(lock,fcntl.LOCK_UN)
for command in [
    ['python3',str(r/'work/solo17/validate.py'),v],
    ['python3',str(r/'work/solo18/pool18.py'),v],
    ['python3',str(r/'work/solo17/scan.py'),'hangs20_c',v,
        '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
        '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']]:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s20c complete648,18378,100pool,six hangs; official requires raw evidence and submission gate.',flush=True)
