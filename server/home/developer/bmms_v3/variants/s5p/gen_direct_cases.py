import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052027)
rows = []
shapes = [(7,13,48),(8,16,128),(16,32,128),(23,73,192),(32,128,256),
          (1,128,256),(3,33,96),(15,17,80),(17,65,144),(31,127,240),
          (32,64,256),(9,15,48),(8,9,64),(7,7,32)]
for batch in [1,4,13,16,21,32]:
    for m,n,k in shapes:
        for dtype in [1,2]:
            typ = np.float16 if dtype == 1 else bfloat16
            for pattern in ['random','negative','cancel']:
                a = rng.uniform(-1,1,(batch,m,k)).astype(typ)
                b = rng.uniform(-1,1,(batch,k,n)).astype(typ)
                if pattern == 'negative':
                    a = np.abs(a).astype(typ); b = -np.abs(b).astype(typ)
                if pattern == 'cancel':
                    half = m//2
                    a[:,half:2*half,:] = -a[:,:half,:]
                    if m%2: a[:,-1,:] = 0
                    b[:,:,:] = b[:,:,:1]
                gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                    d = Path('direct_cases') / f'c{len(rows):04d}'
                    d.mkdir(parents=True,exist_ok=True)
                    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                    gold.tofile(d/'gold.bin')
                    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('direct_cases.txt').write_text('\n'.join(rows)+'\n')
print('GENERATED',len(rows),'direct and fallback cases')
