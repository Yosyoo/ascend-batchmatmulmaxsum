from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s23f'
sha='550bcc0de7aba9d5d524856a446aa98cc567db62ee39300701ad9c3acffa1abe'
out=d/'diagnostic_23f';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]};items=[]
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt',d/'manual_cases18.txt',d/'medium_cases.txt',r/'solo14_data/split16_cases.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),expected=len(manifest.read_text().splitlines()),hashes=hashes);items.append(item)
    (out/'summary.json').write_text(json.dumps(items,indent=2));print(json.dumps(item),flush=True)
    if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
assert sum(x['observed'] for x in items)==648
for fixture_name,label in [('balanced_stress23','balanced_accuracy23f'),('kparallel_batch_stress23','kparallel_batch_accuracy23f'),('kparallel_stress23','kparallel_accuracy23f'),('pair_stress23','pair_accuracy23f'),('long_stress21','long_accuracy23f')]:
    fixture=d/fixture_name;metadata=json.loads((fixture/'fixture_hashes.json').read_text());assert len(metadata)==96
    def check():
        for x in metadata:
            for name,z in x['files'].items():
                p=fixture/f"c{x['case']:03d}"/name
                assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
    check();longout=d/label;longout.mkdir(exist_ok=False)
    p=subprocess.run([str(exe),str(d/(fixture_name+'.txt'))],capture_output=True,text=True,timeout=600)
    (longout/'cases.log').write_text(p.stdout+p.stderr);rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==96 and all(x['passed'] and x['consistent'] for x in rows)
    check();assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
    (longout/'summary.json').write_text(json.dumps(dict(variant=v,passed=good,observed=len(rows),expected=96,hashes=hashes,
        fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),all_fixture_hashes_unchanged=True),indent=2)+'\n')
    print('Long96 stress',good,len(rows),flush=True)
    if not good:raise SystemExit(1)
fcntl.flock(lock,fcntl.LOCK_UN)
specs=['1_512_512_8192_1_0_0','1_512_512_8192_2_0_0','1_128_2048_8192_1_0_0','1_128_2048_8192_2_0_0','1_2048_128_8192_1_0_0','1_2048_128_8192_2_0_0','1_64_512_8192_1_0_0','1_64_512_8192_2_0_0']
for label,variants in [('pilot23_f_parent_base','s23f,s23d,s15i'),('pilot23_base_parent_f','s15i,s23d,s23f')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS candidate diagnostics648,newstress96,longstress96,kparallelstress96,pilots48; not submission ready.',flush=True)
