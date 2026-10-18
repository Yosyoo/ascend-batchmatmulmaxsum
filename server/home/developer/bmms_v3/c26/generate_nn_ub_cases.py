from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/fast_cases');rng=np.random.default_rng(2664001)
shapes=[(8,16,32,128),(1,9,17,32),(3,13,31,40),(21,16,32,48),
        (41,11,23,64),(64,9,7,72),(1,16,16,80),(3,15,32,112),
        (1,1,32,128),(3,7,19,32),(21,16,1,40),(41,9,31,48),
        (64,13,17,72),(1,16,32,120),(3,9,23,88),(21,15,31,104)]
lines=[]
for pattern in ['random','negative','kcancel','mcancel']:
 for B,M,N,K in shapes:
  for dtype,typ in [(1,np.float16),(2,bfloat16)]:
   d=root/('nnub512_'+pattern+f'_{B}_{M}_{N}_{K}_{dtype}');d.mkdir(exist_ok=True)
   a=rng.uniform(-1,1,(B,M,K)).astype(typ)
   b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   if pattern=='kcancel':a[:,:,K//2:]=-a[:,:,:K//2];b[:,K//2:,:]=b[:,:K//2,:]
   if pattern=='mcancel':
    h=M//2;a[:,h:2*h,:]=-a[:,:h,:];b[:,:,:]=b[:,:,:1]
    if M%2:a[:,-1,:]=0
   gold=np.matmul(a.astype(np.float64),b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   a.tofile(d/'a.bin');a.swapaxes(-1,-2).copy().tofile(d/'at.bin')
   b.tofile(d/'b.bin');b.swapaxes(-1,-2).copy().tofile(d/'bt.bin');gold.tofile(d/'gold.bin')
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    case=d/f'{ta}{tb}';case.mkdir(exist_ok=True)
    for name,target in [('x1.bin','at.bin' if ta else 'a.bin'),('x2.bin','bt.bin' if tb else 'b.bin'),('gold.bin','gold.bin')]:
     f=case/name
     if not f.exists():f.symlink_to(d/target)
    lines.append(' '.join(map(str,[B,M,N,K,dtype,ta,tb,case])))
(root/'nnub512.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'cases':len(lines),'shapes':shapes,'patterns':['random','negative','kcancel','mcancel'],'golden':'full actual stored values FP64 matmul -> MaxN -> SumM -> FP32'}),flush=True)
