from pathlib import Path
import subprocess,json,hashlib,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1];sha=sys.argv[2]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
for label in ['narrow_stress33','pad_legal32','pad_stress32','batch_stress30','tile128_stress30','direct_stress32','whole_stress30','short_resident_stress31']:
 fixture=d/label;metadata=json.loads((fixture/'fixture_hashes.json').read_text())
 out=d/f'extra42_{label}_{v}';out.mkdir(exist_ok=False)
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
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good;print('EXTRA42_PASS',label,len(rows),flush=True)
print('EXTRA42_COMPLETE',v,flush=True)
