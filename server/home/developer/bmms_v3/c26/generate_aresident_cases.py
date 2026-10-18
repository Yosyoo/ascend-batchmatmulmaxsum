from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/fast_cases');rng=np.random.default_rng(26601016)
shapes=[(1,4096,1280,1152),(1,2048,1536,1280),(1,8192,512,1024),(2,4096,2048,512),(1,4096,4096,1024),(1,2048,2048,1024),(1,4096,1024,512),(1,8192,256,512)]
lines=[]
for pattern in ['negative','kcancel']:
 for B,M,N,K in shapes:
  scale=np.array([.25,.5,1,2],np.float64)[(np.arange(N)//128)%4]
  for dtype,typ in [(1,np.float16),(2,bfloat16)]:
   d=root/('ares128_'+pattern+f'_{B}_{M}_{N}_{K}_{dtype}');d.mkdir(exist_ok=True)
   a=rng.uniform(-1,1,(B,M,K)).astype(typ)
   v=rng.uniform(.0625,1,(B,K,2)).astype(typ)
   if pattern=='negative':a=np.abs(a).astype(typ);v=-v
   else:a[:,:,K//2:]=-a[:,:,:K//2];v[:,K//2:,:]=v[:,:K//2,:]
   b=(v[:,:,np.arange(N)%2].astype(np.float64)*scale).astype(typ)
   dots=np.matmul(a.astype(np.float64),v.astype(np.float64))
   golden=np.maximum.reduce([dots[:,:,0]*scale[0::2].max(),dots[:,:,0]*scale[0::2].min(),dots[:,:,1]*scale[1::2].max(),dots[:,:,1]*scale[1::2].min()]).sum(-1).astype(np.float32)
   if pattern=='kcancel':assert np.all(dots==0) and np.all(golden==0)
   cols=np.array([0,1,N-2,N-1]);actual=np.matmul(a[:,:4,:].astype(np.float64),b[:,:,cols].astype(np.float64));expected=dots[:,:4,cols%2]*scale[cols]
   assert np.array_equal(actual,expected), (B,M,N,K,dtype,pattern,np.max(np.abs(actual-expected)))
   a.tofile(d/'a.bin');a.swapaxes(-1,-2).copy().tofile(d/'at.bin');b.tofile(d/'b.bin');b.swapaxes(-1,-2).copy().tofile(d/'bt.bin');golden.tofile(d/'gold.bin')
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    case=d/f'{ta}{tb}';case.mkdir(exist_ok=True)
    for name,target in [('x1.bin','at.bin' if ta else 'a.bin'),('x2.bin','bt.bin' if tb else 'b.bin'),('gold.bin','gold.bin')]:
     f=case/name
     if not f.exists():f.symlink_to(d/target)
    lines.append(' '.join(map(str,[B,M,N,K,dtype,ta,tb,case])))
(root/'ares128.txt').write_text('\n'.join(lines)+'\n');print(json.dumps({'cases':len(lines),'shapes':shapes,'patterns':['negative','kcancel'],'golden':'FP64 of actual stored values, rank2 column construction with exact powers-of-two scaling; submatrix checked by directFP64matmul. No full MxN reference materialization.'}),flush=True)
