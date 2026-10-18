from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s23c'
assert not Path('/proc/318239').exists()
assert 'PASS candidate diagnostics648,newstress96,longstress96,kparallelstress96,pilots36' in (d/'run23_c_pilot.log').read_text()
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='44b93c8f5d864c1a2caab02d71d4696ae73be7c3ebc52414ab65d0ea3f789e2f'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
fixture=d/'kparallel_batch_stress23';meta=fixture/'fixture_hashes.json';metadata=json.loads(meta.read_text());assert len(metadata)==96
def check():
    for x in metadata:
        for name,z in x['files'].items():
            p=fixture/f"c{x['case']:03d}"/name
            assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check();out=d/'kparallel_batch_accuracy23c';out.mkdir(exist_ok=False)
p=subprocess.run([str(exe),str(d/'kparallel_batch_stress23.txt')],capture_output=True,text=True,timeout=600)
(out/'cases.log').write_text(p.stdout+p.stderr);rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
good=p.returncode==0 and len(rows)==96 and all(x['passed'] and x['consistent'] for x in rows)
check();assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
(out/'summary.json').write_text(json.dumps(dict(variant=v,passed=good,observed=len(rows),expected=96,hashes=hashes,
    fixture_metadata_sha256=hashlib.sha256(meta.read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True),indent=2)+'\n')
print(json.dumps(dict(passed=good,observed=len(rows))),flush=True)
raise SystemExit(0 if good else 1)
