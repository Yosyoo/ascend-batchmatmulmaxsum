from pathlib import Path
import fcntl,hashlib,json,subprocess,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1];sha=sys.argv[2]
out=d/('stress28_'+v);out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/f'variants/{v}/build/bench_cases';src=r/f'variants/{v}/kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)};items=[]
for fixture_name in ('balanced_stress23','kparallel_batch_stress23','kparallel_stress23','pair_stress23','long_stress21','tiny_stress23'):
 fixture=d/fixture_name;metadata=json.loads((fixture/'fixture_hashes.json').read_text());manifest=d/(fixture_name+'.txt')
 def check():
  for x in metadata:
   for name,z in x['files'].items():
    p=fixture/f"c{x['case']:03d}"/name
    assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
 check();assert len(metadata)==len(manifest.read_text().splitlines())
 p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
 (out/(fixture_name+'.log')).write_text(p.stdout+p.stderr)
 rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
 good=p.returncode==0 and len(rows)==len(metadata) and all(z['passed'] and z['consistent'] for z in rows)
 check();item=dict(fixture=fixture_name,passed=good,expected=len(metadata),observed=len(rows),returncode=p.returncode,
  fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True,
  failures=[z for z in rows if not z['passed'] or not z['consistent']])
 items.append(item);print(json.dumps(item),flush=True)
 (out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,items=items,passed=all(z['passed'] for z in items)),indent=2)+'\n')
 assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
print('STRESS28_COMPLETE '+v,flush=True)
if not all(z['passed'] for z in items):raise SystemExit(1)
