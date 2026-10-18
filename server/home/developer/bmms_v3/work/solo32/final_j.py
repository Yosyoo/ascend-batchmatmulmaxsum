from pathlib import Path
import subprocess,json,hashlib,fcntl,time,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s32j';sha=sys.argv[1]
assert 'SCREEN32_J_COMPLETE' in (d/'screen32_j.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
assert json.loads((d/f'diagnostic32_{v}/summary.json').read_text())['passed']
assert all(z['geometric_mean_ratio']<1 for z in json.loads((d/'quick32_j_00/comparison.json').read_text())['orders'])
assert all(z['geometric_mean_ratio']<1 for z in json.loads((d/'quick32_j_pair/comparison.json').read_text())['orders'])
for label in ['pad_legal32','pad_stress32','batch_stress30','tile128_stress30','direct_stress32','whole_stress30','short_resident_stress31']:
 fixture=d/label;metadata=json.loads((fixture/'fixture_hashes.json').read_text())
 out=d/f'final32_{label}_{v}';out.mkdir(exist_ok=False)
 def check():
  for item in metadata:
   for name,z in item['files'].items():
    p=fixture/f"c{item['case']:03d}"/name
    assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
 check();lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 manifest=d/(label+'.txt');exe=r/f'variants/{v}/build/bench_cases'
 p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
 (out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
 good=p.returncode==0 and len(rows)==len(metadata) and all(z['passed'] and z['consistent'] for z in rows);check()
 (out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(metadata),observed=len(rows),passed=good,
  fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),
  manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),inputs_unchanged=True,
  hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',exe)},
  failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good;print('STRESS32_PASS',label,len(rows),flush=True)
subprocess.run(['python3','work/solo17/validate.py',v],cwd=r,check=True)
subprocess.run(['python3','work/solo28/run_stress.py',v,sha],cwd=r,check=True)
# Preserve the eight historical diagnostic inputs too.
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(r/'work/solo18/fail_8.txt')],cwd=r,capture_output=True,text=True,timeout=900)
(d/'final32_j_fail8.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
assert p.returncode==0 and len(rows)==8 and all(z['passed'] and z['consistent'] for z in rows)
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
deadline=time.monotonic()+1200
while 'BUILD32_J_BENCH_COMPLETE' not in (d/'compile32_j_bench.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
subprocess.run(['python3','work/solo28/pool_compare.py',v,'s32i','pool32_j_i_abba'],cwd=r,check=True)
subprocess.run(['python3','work/solo17/scan.py','hangs32_j',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'],cwd=r,check=True)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
print('FINAL32_J_COMPLETE',flush=True)
