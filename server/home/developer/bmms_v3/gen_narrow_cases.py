import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
rng=np.random.default_rng(1052081);rows=[]
shapes=[(1,1024,16,32),(2,2049,32,64),(1,4096,64,128),(1,8192,64,128),
        (3,1025,128,256),(1,8191,65,128),(2,4097,17,64),(1,1536,127,32)]
for batch,m,n,k in shapes:
 for dtype in [1,2]:
  typ=np.float16 if dtype==1 else bfloat16
  for pattern in ['random','negative','cancel']:
   a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='cancel':
    half=m//2;a[:,half:2*half,:]=-a[:,:half,:]
    if m%2:a[:,-1,:]=0
    b[:,:,:]=b[:,:,:1]
    gold=(a.astype(np.float64)@b[:,:,:1].astype(np.float64)).sum((-2,-1)).astype(np.float32)
   else:gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    d=Path('narrow_cases')/f'c{len(rows):04d}';d.mkdir(parents=True,exist_ok=True)
    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin');gold.tofile(d/'gold.bin')
    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
 print('GENERATED',batch,m,n,k,len(rows),flush=True)
Path('narrow_cases.txt').write_text('\n'.join(rows)+'\n')
