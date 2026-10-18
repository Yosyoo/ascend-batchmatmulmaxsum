import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng=np.random.default_rng(1052111)
shapes=[(16,16,16),(16,32,48),(16,73,128),(16,128,256),
        (8,16,256),(32,16,128),(32,32,16),(32,128,16),
        (32,128,256),(32,73,144),(15,16,128),(17,16,128)]
rows=[]
for batch in [1,2,19,20,21,41]:
    for m,n,k in shapes:
        for dtype in [1,2]:
            typ=np.float16 if dtype==1 else bfloat16
            for pattern in ['random','negative','cancel']:
                a=rng.uniform(-1,1,(batch,m,k)).astype(typ)
                b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
                if pattern=='negative':
                    a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
                if pattern=='cancel':
                    half=m//2
                    a[:,half:2*half,:]=-a[:,:half,:]
                    if m%2:a[:,-1,:]=0
                    b[:,:,:]=b[:,:,:1]
                gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                    d=Path('copy_cases')/f'c{len(rows):04d}';d.mkdir(parents=True,exist_ok=True)
                    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                    gold.tofile(d/'gold.bin')
                    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('copy_cases.txt').write_text('\n'.join(rows)+'\n')
print('GENERATED',len(rows),'copy precision cases',flush=True)
