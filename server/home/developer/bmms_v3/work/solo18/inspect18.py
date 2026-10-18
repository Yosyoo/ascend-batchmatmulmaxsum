from pathlib import Path
import json,hashlib,os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for x in ['pilot_di','pilot_id','pilot_ei']:
    p=d/x/'results.jsonl'
    if p.exists():print(x,[(z['variant'],z['spec'],z['total_warm_us']) for z in map(json.loads,p.read_text().splitlines())])
for v,log in [('s17f','build_fixed.log'),('s17g','build.log')]:
    print(v,(r/'variants'/v/log).read_text()[-1200:])
# Validate the original reference, without producing any submitted output.
checks=[]
for line in (r/'work/solo18/fail_8.txt').read_text().splitlines():
    b,m,n,k,dt,ta,tb=map(int,line.split()[:7]);p=Path(line.split()[7]);assert dt==1
    a=np.fromfile(p/'x1.bin',np.float16).reshape(b,k,m) if ta else np.fromfile(p/'x1.bin',np.float16).reshape(b,m,k)
    c=np.fromfile(p/'x2.bin',np.float16).reshape(b,n,k) if tb else np.fromfile(p/'x2.bin',np.float16).reshape(b,k,n)
    if ta:a=a.swapaxes(-1,-2)
    if tb:c=c.swapaxes(-1,-2)
    gold=np.fromfile(p/'gold.bin',np.float32)
    ref=(a.astype(np.float64)@c.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
    item=dict(path=str(p),gold=gold.tolist(),recomputed_reference=ref.tolist(),matched=bool(np.array_equal(ref,gold)),
        source_inputs_sha256={name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in ['x1.bin','x2.bin','gold.bin']})
    checks.append(item)
(r/'work/solo18/reference_audit.json').write_text(json.dumps(checks,indent=2)+'\n')
print('reference_audit',all(c['matched'] for c in checks),len(checks))
