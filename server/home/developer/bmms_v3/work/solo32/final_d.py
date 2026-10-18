from pathlib import Path
import subprocess,json,hashlib,fcntl,time,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s32d';sha=sys.argv[1]
assert 'SCREEN32_D_COMPLETE' in (d/'screen32_d.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
assert json.loads((d/f'diagnostic32_{v}/summary.json').read_text())['passed']
for layout in ('00','01','10','11'):
 assert all(z['geometric_mean_ratio']<1 for z in json.loads((d/f'quick32_d_{layout}/comparison.json').read_text())['orders'])
subprocess.run(['python3','work/solo17/validate.py',v],cwd=r,check=True)
subprocess.run(['python3','work/solo28/run_stress.py',v,sha],cwd=r,check=True)
for label in ['batch_stress30','tile128_stress30','direct_stress32']:
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
deadline=time.monotonic()+1200
while 'BUILD32_D_BENCH_COMPLETE' not in (d/'compile32_d_bench.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s30p',f'quick32_d_p{ta}{tb}','work/solo31/native_shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
subprocess.run(['python3','work/solo28/pool_compare.py',v,'s30p','pool32_d_p_abba'],cwd=r,check=True)
subprocess.run(['python3','work/solo17/scan.py','hangs32_d',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'],cwd=r,check=True)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
print('FINAL32_D_COMPLETE',flush=True)
