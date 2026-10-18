from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s21d'
sha='00601d4b917ad487200cc7907e6a6adfdbf76d9a820bb8a8e6c47df56f2c272d'
assert hashlib.sha256((r/'variants/s21d/kernel.asc').read_bytes()).hexdigest()==sha
assert 'PASS pilot only' in (d/'run21_d_pilot.log').read_text()
out=d/'long_accuracy21d';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
fixture=d/'long_stress21';manifest=d/'long_stress21.txt';meta=json.loads((fixture/'fixture_hashes.json').read_text())
assert len(meta)==96 and len(manifest.read_text().splitlines())==96
def check_fixtures():
    for x in meta:
        for name,z in x['files'].items():
            p=fixture/f"c{x['case']:03d}"/name
            assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check_fixtures()
exe=r/'variants/s21d/build/bench_cases';src=r/'variants/s21d/kernel.asc'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
(out/'cases.log').write_text(p.stdout+p.stderr)
rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
good=p.returncode==0 and len(rows)==96 and all(x['passed'] and x['consistent'] for x in rows)
check_fixtures();assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
(out/'summary.json').write_text(json.dumps(dict(variant=v,passed=good,observed=len(rows),expected=96,hashes=hashes,
    fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True),indent=2)+'\n')
print('long stress',good,len(rows),flush=True)
if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
fcntl.flock(lock,fcntl.LOCK_UN)
p=subprocess.run(['python3',str(r/'work/solo21/run_d_final.py')]);raise SystemExit(p.returncode)
