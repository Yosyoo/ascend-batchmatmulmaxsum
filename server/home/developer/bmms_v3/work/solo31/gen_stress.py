"""CPU generates immutable reference fixtures only. Every output tested is NPU-computed."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,numpy as np
from ml_dtypes import bfloat16
r=Path('/home/developer/bmms_v3');d=r/'solo17_data/short_resident_stress31';d.mkdir(exist_ok=False)
rng=np.random.default_rng(2026101431);rows=[];metadata=[]
for batch,m,n,k in [(1,512,4096,32),(1,2048,1024,128),(1,1024,2048,128),(1,8192,512,64)]:
 for dtype in (1,2):
  typ=np.float16 if dtype==1 else bfloat16
  for pattern in ('random','negative','cancel_m','cancel_k'):
   a=rng.uniform(-1,1,(batch,m,k)).astype(typ);b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='cancel_m':a[:,m//2:,:]=-a[:,:m//2,:];b[:,:,:]=b[:,:,:1]
   if pattern=='cancel_k':a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
    case=d/f'c{len(rows):03d}';case.mkdir()
    (a.swapaxes(-1,-2).copy() if ta else a).tofile(case/'x1.bin')
    (b.swapaxes(-1,-2).copy() if tb else b).tofile(case/'x2.bin');gold.tofile(case/'gold.bin')
    rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,case))))
    metadata.append(dict(case=len(rows)-1,shape=[batch,m,n,k],dtype=dtype,ta=ta,tb=tb,pattern=pattern,
     files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in case.iterdir()}))
 print('GENERATED',batch,m,n,k,flush=True)
assert len(rows)==128
(r/'solo17_data/short_resident_stress31.txt').write_text('\n'.join(rows)+'\n')
(d/'fixture_hashes.json').write_text(json.dumps(metadata,indent=2)+'\n')
print('GENERATED_128_SHORT_RESIDENT_STRESS',flush=True)
