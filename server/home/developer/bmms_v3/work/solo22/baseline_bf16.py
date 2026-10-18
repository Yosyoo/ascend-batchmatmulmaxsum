"""Datatype cost audit only; original full precision failures remain failures."""
from pathlib import Path
import fcntl, hashlib, json, subprocess, time
r=Path('/home/developer/bmms_v3'); d=r/'solo17_data'; w=r/'work/solo22'
out=d/'baseline_bf16_22'; out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=r/'variants/s15i/build/bench_cases'; src=r/'variants/s15i/kernel.asc'
expected='b67d45e1b270ad416e403cd18a7e9f0cd06341f26e8e734f1dee4fdc8e37c4f6'
assert hashlib.sha256(src.read_bytes()).hexdigest()==expected
hashes={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
fixture=d/'long_stress21'; meta=json.loads((fixture/'fixture_hashes.json').read_text())
manifest=(d/'long_stress21.txt').read_text().splitlines()
assert len(meta)==len(manifest)==96
def check_fixtures():
    for x in meta:
        for name,z in x['files'].items():
            p=fixture/f"c{x['case']:03d}"/name
            assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check_fixtures(); selected=[x for x in meta if x['dtype']==2]; assert len(selected)==48
items=[]
for x in selected:
    case=x['case']; mf=out/f'case_{case:03d}.txt'; mf.write_text(manifest[case]+'\n')
    p=subprocess.run([str(exe),str(mf)],capture_output=True,text=True,timeout=60)
    (out/f'case_{case:03d}.log').write_text(p.stdout+p.stderr)
    rows=[json.loads(s) for s in p.stdout.splitlines() if s.startswith('{')]
    good=p.returncode==0 and len(rows)==1 and rows[0]['passed'] and rows[0]['consistent']
    item=dict(original_case=case,shape=x['shape'],dtype=x['dtype'],ta=x['ta'],tb=x['tb'],pattern=x['pattern'],
              passed=good,returncode=p.returncode,results=rows)
    items.append(item); (out/'results.json').write_text(json.dumps(items,indent=2)+'\n')
    print(json.dumps(item),flush=True)
check_fixtures(); assert hashes=={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
summary=dict(variant='s15i',audit='BF16 component of immutable full96 stress set',expected=48,observed=len(items),
             passed=sum(x['passed'] for x in items),failed=sum(not x['passed'] for x in items),
             hashes=hashes,fixture_metadata_sha256=hashlib.sha256((fixture/'fixture_hashes.json').read_bytes()).hexdigest(),
             all96_fixture_hashes_unchanged=True,original_fp16_failures_unresolved=True,
             precision_tolerance='1e-4 + 1e-4 * abs(gold)',executions_per_case=3)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary),flush=True)
