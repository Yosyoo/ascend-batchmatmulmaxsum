from pathlib import Path
import subprocess,time,json,hashlib,fcntl
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s30n';sha='5152d6d02c014d29665ee7154c2985c3c6b2b1c30554f38f0d275c9bc35739c8'
deadline=time.monotonic()+1500
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile30_n.log').read_text(errors='replace') or 'GENERATED_512_WHOLE_STRESS' not in (d/'gen30_whole.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 assert 'error:' not in (d/'compile30_n.log').read_text(errors='replace')
 time.sleep(5)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
out=d/'diagnostic30_s30n';out.mkdir(exist_ok=False)
fixtures=d/'whole_stress30';meta=fixtures/'fixture_hashes.json';meta_sha=hashlib.sha256(meta.read_bytes()).hexdigest()
metadata=json.loads(meta.read_text())
def check():
 assert hashlib.sha256(meta.read_bytes()).hexdigest()==meta_sha
 for item in metadata:
  for name,z in item['files'].items():
   p=fixtures/f"c{item['case']:03d}"/name
   assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check()
origins=[d/'diagnostic30_s30l/cases.txt',d/'whole_stress30.txt']
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in origins}
lines=sum([p.read_text().splitlines() for p in origins],[]);manifest=out/'cases.txt';manifest.write_text('\n'.join(lines)+'\n')
manifest_sha=hashlib.sha256(manifest.read_bytes()).hexdigest();assert len(lines)==552
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (exe,r/f'variants/{v}/kernel.asc')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
check();assert before=={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in origins}
assert manifest_sha==hashlib.sha256(manifest.read_bytes()).hexdigest()
good=p.returncode==0 and len(rows)==len(lines) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,origin_hashes=before,fixture_metadata_sha256=meta_sha,
 expected=len(lines),observed=len(rows),passed=good,inputs_unchanged=True,manifest_sha256=manifest_sha,
 failures=[z for z in rows if not z['passed'] or not z['consistent']],returncode=p.returncode),indent=2)+'\n')
print('PRECISION30_N',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
subprocess.run(['python3','work/solo28/quick_compare.py',v,'s29m','quick30_n','work/solo30/n_shapes.txt'],cwd=r,check=True)
print('SCREEN30_N_COMPLETE',flush=True)
