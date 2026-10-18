from pathlib import Path
import subprocess,json,time,hashlib,fcntl
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s30p';sha='27bdef5b733320408f9179c8de1b74ee9b36df9801214d47c10bb2310fc1941c'
assert 'SCREEN30_P_COMPLETE' in (d/'screen30_p.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
assert json.loads((d/'diagnostic30_s30p/summary.json').read_text())['passed']
assert all(z['geometric_mean_ratio']<1 for z in json.loads((d/'quick30_p/comparison.json').read_text())['orders'])
for label in ['batch','tile128']:
 fixture=d/f'{label}_stress30';metadata=json.loads((fixture/'fixture_hashes.json').read_text())
 out=d/f'stress30_{label}_{v}';out.mkdir(exist_ok=False)
 def check():
  for item in metadata:
   for name,z in item['files'].items():
    p=fixture/f"c{item['case']:03d}"/name
    assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
 check();lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
 p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(d/f'{label}_stress30.txt')],cwd=r,capture_output=True,text=True,timeout=900)
 (out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
 good=p.returncode==0 and len(rows)==320 and all(z['passed'] and z['consistent'] for z in rows);check()
 (out/'summary.json').write_text(json.dumps(dict(variant=v,total=len(rows),passed=good,hashes_unchanged=True,
  fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),
  hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',r/f'variants/{v}/build/bench_cases')},
  failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good;print('STRESS30_'+label+'_320_PASS',flush=True)
for cmd in [['python3','work/solo17/validate.py',v],['python3','work/solo28/run_stress.py',v,sha],
 ['python3','work/solo28/pool_compare.py',v,'s29m','pool30_p_base_abba']]:
 print('START',cmd,flush=True);subprocess.run(cmd,cwd=r,check=True)
deadline=time.monotonic()+1200
while 'BUILD30_P_BENCH_COMPLETE' not in (d/'compile30_p_bench.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
subprocess.run(['python3','work/solo17/scan.py','hangs30_p',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'],cwd=r,check=True)
print('FINAL30_P_COMPLETE',flush=True)
