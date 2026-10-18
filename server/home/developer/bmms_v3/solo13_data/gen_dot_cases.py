import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rows=[]
for seed in [1052113,1052114]:
    rng=np.random.default_rng(seed)
    for batch in [1,2,4,19,20,21,39,40,41,64]:
        for dtype in [1,2]:
            typ=np.float16 if dtype==1 else bfloat16
            for pattern in ['random','negative','cancel','zero','rounding']:
                a=rng.uniform(-1,1,(batch,1,32)).astype(typ)
                b=rng.uniform(-1,1,(batch,32,1)).astype(typ)
                if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
                if pattern=='cancel':
                    a[:,:,16:]=-a[:,:,:16]
                    b[:,16:,:]=b[:,:16,:]
                if pattern=='zero':a.fill(0)
                if pattern=='rounding':
                    a=(1+rng.uniform(-.02,.02,a.shape)).astype(typ)
                    b=(1+rng.uniform(-.02,.02,b.shape)).astype(typ)
                    b[:,16:,:]=-b[:,16:,:]
                gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                    d=Path('dot_cases')/f'c{len(rows):04d}';d.mkdir(parents=True,exist_ok=True)
                    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                    gold.tofile(d/'gold.bin')
                    rows.append(' '.join(map(str,(batch,1,1,32,dtype,ta,tb,d.resolve()))))
Path('dot_cases.txt').write_text('\n'.join(rows)+'\n')
print('GENERATED',len(rows),'dot precision cases',flush=True)
