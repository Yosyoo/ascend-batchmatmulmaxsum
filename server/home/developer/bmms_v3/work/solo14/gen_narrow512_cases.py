import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052415)
rows = []
for batch, m in [(1,7680),(1,8192),(1,10240),(1,12288),(1,16384),(2,4096),(4,4096),(1,8193),(1,6144),(1,32768)]:
    n,k=64,128
    for dtype in [1,2]:
        typ = np.float16 if dtype == 1 else bfloat16
        for pattern in ['random','negative','cancel']:
            a = rng.uniform(-1,1,(batch,m,k)).astype(typ)
            b = rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern == 'negative':
                a = np.abs(a).astype(typ)
                b = -np.abs(b).astype(typ)
            if pattern == 'cancel':
                h = m//2
                a[:,h:2*h,:] = -a[:,:h,:]
                if m % 2:
                    a[:,-1,:] = 0
                b[:,:,:] = b[:,:,:1]
            gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d = Path('narrow512_cases') / f'c{len(rows):04d}'
                d.mkdir(parents=True, exist_ok=True)
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin')
                rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('narrow512_cases.txt').write_text('\n'.join(rows)+'\n')
assert len(rows) == 240
print('GENERATED',len(rows),'narrow512 and fallback cases',flush=True)
