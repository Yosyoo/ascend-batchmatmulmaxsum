from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s26b';out=d/'diagnostic_28_s26b';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/f'variants/{v}/build/bench_cases';src=r/f'variants/{v}/kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='4b214cd4e162bd2c18340e14bffe70376d93d7df3bfb99ceb9e5968bff1060d4'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
items=[]
for label,manifest in [('medium_cases',d/'medium_cases.txt'),('split16_cases',r/'solo14_data/split16_cases.txt')]:
 before=hashlib.sha256(manifest.read_bytes()).hexdigest();expected=len(manifest.read_text().splitlines())
 p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
 (out/(label+'.log')).write_text(p.stdout+p.stderr)
 rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
 good=p.returncode==0 and len(rows)==expected and all(z['passed'] and z['consistent'] for z in rows)
 assert before==hashlib.sha256(manifest.read_bytes()).hexdigest()
 item=dict(suite=label,manifest=str(manifest),manifest_sha256=before,expected=expected,observed=len(rows),passed=good,returncode=p.returncode,
  failures=[z for z in rows if not z['passed'] or not z['consistent']])
 items.append(item);print(json.dumps(item),flush=True)
 (out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,suites=items,passed=all(z['passed'] for z in items)),indent=2)+'\n')
assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
print('AUDIT28_COMPLETE',flush=True)
