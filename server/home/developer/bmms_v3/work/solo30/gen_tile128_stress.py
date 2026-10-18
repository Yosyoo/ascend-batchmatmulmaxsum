"""Additional validation references only; the NPU computes every tested operator output."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json
import numpy as np
from ml_dtypes import bfloat16
r=Path('/home/developer/bmms_v3');d=r/'solo17_data/tile128_stress30';d.mkdir(exist_ok=False)
rng=np.random.default_rng(2026101452);rows=[];metadata=[]
for batch,m,n,k in [(batch,128,128,k) for batch in [1,8,21,64,127] for k in [64,128]]:
    for dtype in [1,2]:
        typ=np.float16 if dtype==1 else bfloat16
        for pattern in ['random','negative','cancel_m','cancel_k']:
            a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
            if pattern=='cancel_m':a[:,m//2:,:]=-a[:,:m//2,:];b[:,:,:]=b[:,:,:1]
            if pattern=='cancel_k':a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
            # CPU reference has no role in operator execution or performance measurement.
            gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                case=d/f'c{len(rows):03d}';case.mkdir()
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(case/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(case/'x2.bin');gold.tofile(case/'gold.bin')
                rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,case))))
                metadata.append(dict(case=len(rows)-1,shape=[batch,m,n,k],dtype=dtype,ta=ta,tb=tb,pattern=pattern,
                    files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in case.iterdir()}))
            print('generated',m,n,k,dtype,pattern,flush=True)
assert len(rows)==320
(r/'solo17_data/tile128_stress30.txt').write_text('\n'.join(rows)+'\n')
(d/'fixture_hashes.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('PASS generated320 immutable validation fixtures',flush=True)
