import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
rng=np.random.default_rng(1052417)
rows=[]
specs=[(1,7680,64,128),(1,8192,64,128),(2,4096,64,128),(4,4096,64,128),
       (1,5133,47,48),(2,3072,33,112),(1,6144,63,64),(2,2048,64,32),
       (1,7168,64,128),(1,8192,33,128),(1,8192,47,112),(4,8192,64,128)]
for batch,m,n,k in specs:
 assert max(m,n,k)<=8192 and k>=32 and k%8==0 and batch*m*k<=2**26 and batch*n*k<=2**26
 for dtype in [1,2]:
  typ=np.float16 if dtype==1 else bfloat16
  for pattern in ['random','negative','cancel_m','cancel_k']:
   a=rng.uniform(-1,1,(batch,m,k)).astype(typ)
   b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='cancel_m':
    h=m//2;a[:,h:2*h,:]=-a[:,:h,:];b[:,:,:]=b[:,:,:1]
    if m%2:a[:,-1,:]=0
   if pattern=='cancel_k':a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    d=Path('balanced_cases')/f'c{len(rows):03d}';d.mkdir(parents=True,exist_ok=True)
    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
    gold.tofile(d/'gold.bin');rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
Path('balanced_cases.txt').write_text('\n'.join(rows)+'\n')
assert len(rows)==384
print('GENERATED',len(rows),'official-range balanced narrow cases',flush=True)
