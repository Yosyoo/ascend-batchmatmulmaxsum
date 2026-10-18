from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/fast_cases');rng=np.random.default_rng(26621016);lines=[]
for pattern in ['random','cancel']:
 for B in [1,3,19,41,64]:
  for K in [32,48,64]:
   for dtype,typ in [(1,np.float16),(2,bfloat16)]:
    d=root/f'dot240_{pattern}_{B}_{K}_{dtype}';d.mkdir(exist_ok=True)
    a=rng.uniform(-1,1,(B,1,K)).astype(typ);b=rng.uniform(-1,1,(B,K,1)).astype(typ)
    if pattern=='cancel':a[:,:,K//2:]=-a[:,:,:K//2];b[:,K//2:,:]=b[:,:K//2,:]
    if pattern=='random' and B==41:a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
    golden=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
    a.tofile(d/'a.bin');b.tofile(d/'b.bin');golden.tofile(d/'gold.bin')
    for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
     case=d/f'{ta}{tb}';case.mkdir(exist_ok=True)
     for name,target in [('x1.bin','a.bin'),('x2.bin','b.bin'),('gold.bin','gold.bin')]:
      f=case/name
      if not f.exists():f.symlink_to(d/target)
     lines.append(' '.join(map(str,[B,1,1,K,dtype,ta,tb,case])))
(root/'dot240.txt').write_text('\n'.join(lines)+'\n');print(json.dumps({'cases':len(lines),'B':[1,3,19,41,64],'K':[32,48,64],'patterns':['random','K-half cancellation'],'golden':'FP64 actual storedinput ->FP32','negative_batch':41}),flush=True)
