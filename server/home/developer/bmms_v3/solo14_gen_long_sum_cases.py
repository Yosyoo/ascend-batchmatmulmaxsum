import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
rng=np.random.default_rng(1052416)
rows=[]
for m in [12288,16384,17536]:
 n,k,batch=128,16,1
 for dtype in [1,2]:
  typ=np.float16 if dtype==1 else bfloat16
  for pattern in ['random','negative','cancel']:
   a=rng.uniform(-1,1,(batch,m,k)).astype(typ)
   b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='cancel':a[:,m//2:,:]=-a[:,:m//2,:];b[:,:,:]=b[:,:,:1]
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    d=Path('long_sum_cases')/f'c{len(rows):03d}';d.mkdir(parents=True,exist_ok=True)
    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
    gold.tofile(d/'gold.bin')
    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('long_sum_cases.txt').write_text('\n'.join(rows)+'\n')
assert len(rows)==72
print('GENERATED',len(rows),'long M sum boundary cases',flush=True)
