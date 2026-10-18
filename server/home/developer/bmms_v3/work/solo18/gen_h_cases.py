"""Validation-only stress for the newly resident half-K path, CPU reference only."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
r=Path('/home/developer/bmms_v3');out=r/'solo17_data/resident_cases18';out.mkdir(exist_ok=False)
rng=np.random.default_rng(2026100918);rows=[]
for k in [1152,1536,1792]:
    batch,m,n=1,512,1024
    for dtype in [1,2]:
        typ=np.float16 if dtype==1 else bfloat16
        for pattern in ['random','negative','cancel_m','cancel_k']:
            a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
            if pattern=='cancel_m':a[:,m//2:,:]=-a[:,:m//2,:];b[:,:,:]=b[:,:,:1]
            if pattern=='cancel_k':a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
            gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d=out/f'c{len(rows):03d}';d.mkdir()
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin');rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d))))
            print('generated',k,dtype,pattern,flush=True)
(r/'solo17_data/resident_cases18.txt').write_text('\n'.join(rows)+'\n');assert len(rows)==96
print('PASS generated 96 resident accuracy cases')
