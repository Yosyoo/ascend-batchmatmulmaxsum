"""Precision coverage for the NZ prepack gate and its padded storage boundaries."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052082)
rows = []
shapes = [(2,513,769,776), (3,1025,1031,1032), (1,512,512,520),
          (2,1024,1023,1032), (1,1025,1281,1048), (1,2048,1025,1032),
          (1,4096,513,2040), (1,511,513,520)]
for batch,m,n,k in shapes:
    for dtype in [1,2]:
        typ = np.float16 if dtype == 1 else bfloat16
        for pattern in ['random','negative','cancel']:
            a = rng.uniform(-1,1,(batch,m,k)).astype(typ)
            b = rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern == 'negative':
                a = np.abs(a).astype(typ)
                b = -np.abs(b).astype(typ)
            if pattern == 'cancel':
                half = m//2
                a[:,half:2*half,:] = -a[:,:half,:]
                if m%2: a[:,-1,:] = 0
                b[:,:,:] = b[:,:,:1]
                gold = (a.astype(np.float64) @ b[:,:,:1].astype(np.float64)).sum((-2,-1)).astype(np.float32)
            else:
                gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d = Path('nz_cases') / f'c{len(rows):04d}'
                d.mkdir(parents=True,exist_ok=True)
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin')
                rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
    print('GENERATED',batch,m,n,k,len(rows),flush=True)
Path('nz_cases.txt').write_text('\n'.join(rows)+'\n')
