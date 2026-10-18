import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052028)
rows = []
shapes = [(1,512,513,520),(1,513,1031,1032),(1,1025,1031,1032),
          (1,2048,1025,1032),(2,513,769,776),(1,1024,1023,1032)]
for batch,m,n,k in shapes:
    for dtype in [1,2]:
        typ = np.float16 if dtype == 1 else bfloat16
        for pattern in ['random','negative']:
            a = rng.uniform(-1,1,(batch,m,k)).astype(typ)
            b = rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern == 'negative':
                a = np.abs(a).astype(typ); b = -np.abs(b).astype(typ)
            gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d = Path('tail_cases') / f'c{len(rows):03d}'
                d.mkdir(parents=True,exist_ok=True)
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin')
                rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('tail_cases.txt').write_text('\n'.join(rows)+'\n')
print('GENERATED',len(rows),'large tail cases')
