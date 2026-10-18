"""Accuracy fixtures only; every operator output is computed by the NPU executable."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
out=Path('/home/developer/bmms_v3/solo17_data');rng=np.random.default_rng(2026100917)
specs=[(1,512,512,1040),(1,512,640,1152),(2,512,512,1520),(1,640,512,1536),
       (1,512,512,1792),(1,512,512,1808),(1,512,512,2032),(1,513,641,1536)]
rows=[]
for batch,m,n,k in specs:
    for dtype in [1,2]:
        typ=np.float16 if dtype==1 else bfloat16
        for pattern in ['random','negative','cancel_m','cancel_k']:
            a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
            if pattern=='cancel_m':
                half=m//2;a[:,half:2*half,:]=-a[:,:half,:];b[:,:,:]=b[:,:,:1]
                if m%2:a[:,-1,:]=0
            if pattern=='cancel_k':
                a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
            # Reference is validation-only; never linked or passed to the NPU operator.
            gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d=out/'medium_cases'/f'c{len(rows):03d}';d.mkdir(parents=True,exist_ok=True)
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin');rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d))))
            print('generated',batch,m,n,k,dtype,pattern,flush=True)
(out/'medium_cases.txt').write_text('\n'.join(rows)+'\n')
assert len(rows)==256
print('PASS generated 256 accuracy fixtures',flush=True)
