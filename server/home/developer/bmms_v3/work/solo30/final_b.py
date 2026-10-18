from pathlib import Path
import subprocess,json,time,hashlib,fcntl,os
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s30b'
assert 'ROUND30_AB_COMPLETE' in (d/'screen30_ab.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()=='277434e25e6353ef8a695544253cf43c2eced14b97e3cfe9c5dbe03ab5878a34'
comparison=json.loads((d/'quick30_b/comparison.json').read_text());assert all(z['geometric_mean_ratio']<.9 for z in comparison['orders'])
subprocess.run(['python3','work/solo30/gen_batch_stress.py'],cwd=r,check=True)
out=d/'stress30_batch_s30b';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
fixture=d/'batch_stress30';metadata=json.loads((fixture/'fixture_hashes.json').read_text())
def check():
 for item in metadata:
  for name,z in item['files'].items():
   p=fixture/f"c{item['case']:03d}"/name
   assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check()
p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(d/'batch_stress30.txt')],cwd=r,capture_output=True,text=True,timeout=600)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==320 and all(z['passed'] and z['consistent'] for z in rows);check()
(out/'summary.json').write_text(json.dumps(dict(variant=v,total=len(rows),passed=good,hashes_unchanged=True,
 fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',r/f'variants/{v}/build/bench_cases')},
 failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
assert good,(p.returncode,rows[-1:] if rows else p.stderr)
fcntl.flock(lock,fcntl.LOCK_UN);lock.close();print('NEW_BATCH_STRESS30_320_PASS',flush=True)
for cmd in [['python3','work/solo17/validate.py',v],['python3','work/solo28/run_stress.py',v,'277434e25e6353ef8a695544253cf43c2eced14b97e3cfe9c5dbe03ab5878a34'],
 ['python3','work/solo28/pool_compare.py',v,'s29m','pool30_b_base_abba']]:
 print('START',cmd,flush=True);subprocess.run(cmd,cwd=r,check=True)
deadline=time.monotonic()+1200
while 'BUILD30_B_BENCH_COMPLETE' not in (d/'compile30_b_bench.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
subprocess.run(['python3','work/solo17/scan.py','hangs30_b',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'],cwd=r,check=True)
print('FINAL30_B_COMPLETE',flush=True)
