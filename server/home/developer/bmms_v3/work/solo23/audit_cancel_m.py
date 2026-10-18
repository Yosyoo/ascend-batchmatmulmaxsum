from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert not Path('/proc/349999').exists()
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
out=d/'cancel_m_audit23';out.mkdir(exist_ok=False)
fixture=d/'balanced_stress23';metadata=json.loads((fixture/'fixture_hashes.json').read_text())
manifest=(d/'balanced_stress23.txt').read_text().splitlines();assert len(metadata)==len(manifest)==96
def check():
    for x in metadata:
        for name,z in x['files'].items():
            p=fixture/f"c{x['case']:03d}"/name
            assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check();items=[]
for v in ['s23f','s23d','s15i']:
    exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
    for i in [72,88,89,90,91,92]:
        one=out/f'{v}_{i}.txt';one.write_text(manifest[i]+'\n')
        p=subprocess.run([str(exe),str(one)],capture_output=True,text=True,timeout=120)
        (out/f'{v}_{i}.log').write_text(p.stdout+p.stderr)
        rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')];assert len(rows)==1
        x=rows[0];assert x['consistent']
        item=dict(variant=v,fixture_case=i,pattern=metadata[i]['pattern'],passed=x['passed'],measurement=x,hashes=hashes,returncode=p.returncode)
        items.append(item);(out/'summary.json').write_text(json.dumps(items,indent=2)+'\n');print(json.dumps(item),flush=True)
    assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
check();assert len(items)==18
(out/'integrity.json').write_text(json.dumps(dict(fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True,observed=18,failed=sum(not x['passed'] for x in items)),indent=2)+'\n')
print('PASS audit completed18; failures retained; precision tolerance unchanged.',flush=True)
