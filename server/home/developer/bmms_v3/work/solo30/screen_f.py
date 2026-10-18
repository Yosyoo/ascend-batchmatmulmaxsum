from pathlib import Path
import subprocess,time,json,hashlib,fcntl,os
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s30f';sha='1d5583d35ba170229dc98a186cb2a6bbb5f3abffd86f2894ba740c302018efc0'
deadline=time.monotonic()+1200
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile30_f.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 assert 'error:' not in (d/'compile30_f.log').read_text(errors='replace')
 time.sleep(5)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
subprocess.run(['python3','work/solo30/gen_tile128_stress.py'],cwd=r,check=True)
out=d/'diagnostic30_s30f';out.mkdir(exist_ok=False)
fixture=d/'tile128_stress30';metadata=json.loads((fixture/'fixture_hashes.json').read_text())
def check():
 for item in metadata:
  for name,z in item['files'].items():
   p=fixture/f"c{item['case']:03d}"/name
   assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check()
manifests=[d/'tile128_stress30.txt',r/'work/solo18/fail_8.txt']
cases=out/'cases.txt';cases.write_text(''.join(p.read_text() for p in manifests))
case_sha=hashlib.sha256(cases.read_bytes()).hexdigest()
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (exe,r/f'variants/{v}/kernel.asc')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
p=subprocess.run([str(exe),str(cases)],cwd=r,capture_output=True,text=True,timeout=600)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==328 and all(z['passed'] and z['consistent'] for z in rows);check()
assert case_sha==hashlib.sha256(cases.read_bytes()).hexdigest()
summary=dict(variant=v,hashes=hashes,manifest_sha256=case_sha,total=len(rows),expected=328,passed=good,
 fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True,
 failures=[z for z in rows if not z['passed'] or not z['consistent']],returncode=p.returncode)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
subprocess.run(['python3','work/solo28/quick_compare.py',v,'s30b','quick30_f','work/solo30/e_shapes.txt'],cwd=r,check=True)
print('SCREEN30_F_COMPLETE',flush=True)
