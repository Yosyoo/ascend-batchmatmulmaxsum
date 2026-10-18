from pathlib import Path
import json,hashlib,subprocess,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';w=r/'work/solo43';v='s43a';sha=sys.argv[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(r/f'variants/{v}/kernel.asc')==sha
lockspec=json.loads((w/'experiment_a_lock.json').read_text())
for name,value in lockspec['hashes'].items():assert digest(w/name)==value
for origin in lockspec['origins']:assert digest(Path(origin['manifest']))==origin['sha256']
manifest=w/'packed_cases.txt';lines=manifest.read_text().splitlines();assert len(lines)==200
out=d/'diagnostic43_s43a';out.mkdir(exist_ok=False)
exe=r/f'variants/{v}/build/bench_cases'
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,cwd=r,timeout=300)
(out/'precision.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==len(lines) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(lines),observed=len(rows),passed=good,returncode=p.returncode,manifest_sha256=digest(manifest),hashes={p.name:digest(p) for p in (r/f'variants/{v}/kernel.asc',exe)},failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2))
print('PRECISION43_A',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
for dtype,ta,tb in [(1,0,0),(1,0,1),(1,1,0),(1,1,1),(2,0,0),(2,0,1),(2,1,0),(2,1,1)]:
    label=f'quick43_a_{dtype}{ta}{tb}'
    subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s41c',label,str(w/'packed_shapes.txt'),str(dtype),str(ta),str(tb)],cwd=r,check=True)
    if dtype==1 and ta==0 and tb==0:
        comp=json.loads((d/label/'comparison.json').read_text());a,b=comp['orders']
        qualifying=all(x['geometric_mean_ratio']<=.98 for x in comp['orders']) and not any(x['ratio']>1.03 and y['ratio']>1.03 for x,y in zip(a['ratios'],b['ratios']))
        print('SCREEN43_A_QUALIFY',qualifying,flush=True)
        if not qualifying:break
print('SCREEN43_A_COMPLETE',flush=True)
