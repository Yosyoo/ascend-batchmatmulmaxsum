from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/fast_cases');rng=np.random.default_rng(26571017)
shapes=[(1,528,1280,784),(1,1040,640,1040),(1,768,2048,1552),(1,1040,528,528),(3,1024,1280,1168),(1,512,2560,1776)]
lines=[]
for pattern in ['random','mcancel']:
 for shape in shapes:
  B,M,N,K=shape
  for dtype,typ in [(1,np.float16),(2,bfloat16)]:
   d=root/('bres96_'+pattern+'_'+'_'.join(map(str,shape))+f'_{dtype}');d.mkdir(exist_ok=True)
   a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if pattern=='mcancel':a[:,M//2:,:]=-a[:,:M//2,:];b[:,:,:]=b[:,:,:1]
   if pattern=='random' and shape==(1,1040,528,528):a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   a.tofile(d/'a.bin');a.swapaxes(-1,-2).copy().tofile(d/'at.bin');b.tofile(d/'b.bin');b.swapaxes(-1,-2).copy().tofile(d/'bt.bin');gold.tofile(d/'gold.bin')
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    case=d/f'{ta}{tb}';case.mkdir(exist_ok=True)
    for name,target in [('x1.bin','at.bin' if ta else 'a.bin'),('x2.bin','bt.bin' if tb else 'b.bin'),('gold.bin','gold.bin')]:
     f=case/name
     if not f.exists():f.symlink_to(d/target)
    lines.append(' '.join(map(str,[B,M,N,K,dtype,ta,tb,case])))
(root/'bres96.txt').write_text('\n'.join(lines)+'\n');print(json.dumps({'cases':len(lines),'shapes':shapes,'patterns':['random','mcancel'],'negative_random_shape':[1,1040,528,528],'golden':'FP64 of actual stored inputs ->FP32'}),flush=True)
