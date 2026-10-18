import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np,json,hashlib
from ml_dtypes import bfloat16
r=Path('/home/developer/bmms_v3');d=r/'solo17_data/pad_stress32';d.mkdir(exist_ok=False)
shapes=[(3,17,19,17),(2,24,33,23),(4,33,65,31),(1,48,48,33),
(2,64,64,63),(3,65,129,65),(1,96,96,71),(2,127,127,72),
(1,128,128,127),(2,129,129,129),(1,255,255,239),(2,256,256,255)]
rng=np.random.default_rng(2026101532);rows=[];metadata=[]
for batch,m,n,k in shapes:
 for dtype in (1,2):
  typ=np.float16 if dtype==1 else bfloat16
  for pattern in ('random','negative','cancel_m','cancel_k'):
   a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='cancel_m':
    pairs=m//2;a[:,pairs:2*pairs,:]=-a[:,:pairs,:];b[:,:,:]=b[:,:,:1]
   if pattern=='cancel_k':
    q=k//2;a[:,:,q:2*q]=a[:,:,:q];b[:,q:2*q,:]=-b[:,:q,:]
    if k%2:a[:,:,-1]=0;b[:,-1,:]=0
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   for ta,tb in ((0,0),):
    case=d/f'c{len(rows):03d}';case.mkdir()
    (a.swapaxes(-1,-2).copy() if ta else a).tofile(case/'x1.bin')
    (b.swapaxes(-1,-2).copy() if tb else b).tofile(case/'x2.bin');gold.tofile(case/'gold.bin')
    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,case))))
    metadata.append(dict(case=len(rows)-1,shape=[batch,m,n,k],dtype=dtype,ta=ta,tb=tb,pattern=pattern,
     files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in case.iterdir()}))
(r/'solo17_data/pad_stress32.txt').write_text('\n'.join(rows)+'\n')
(d/'fixture_hashes.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('GENERATED_96_PAD_STRESS',len(rows),flush=True)
