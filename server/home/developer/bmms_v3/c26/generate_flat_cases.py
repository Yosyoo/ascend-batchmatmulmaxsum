"""Correctness fixtures only. No performance inference from this harness."""
from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16

root=Path('/home/developer/bmms_v3/c26/fast_cases')
root.mkdir(exist_ok=True)
large=[(1,2048,1536,1280),(1,4096,1280,1152),(1,1536,2048,2048),(2,768,1024,512),(1,641,1137,768),(1,1280,4096,1536)]
negative=[(2,768,1024,512)]
rng=np.random.default_rng(26421016)
all_lines=[];groups={}
for group,shapes in [('flat_random48',large),('flat_cancel32',large[:4])]:
 lines=[]
 for shape in shapes:
  B,M,N,K=shape
  for dtype,typ in [(1,np.float16),(2,bfloat16)]:
   d=root/(group+'_'+'_'.join(map(str,shape))+f'_{dtype}');d.mkdir(exist_ok=True)
   a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if group=='flat_cancel32':
    a[:,M//2:,:]=-a[:,:M//2,:];b[:,:,:]=b[:,:,:1]
   if group=='flat_random48' and shape in negative:a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   a.tofile(d/'a.bin');a.swapaxes(-1,-2).copy().tofile(d/'at.bin')
   b.tofile(d/'b.bin');b.swapaxes(-1,-2).copy().tofile(d/'bt.bin');gold.tofile(d/'gold.bin')
   for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
    case=d/f'{ta}{tb}';case.mkdir(exist_ok=True)
    for name,target in [('x1.bin','at.bin' if ta else 'a.bin'),('x2.bin','bt.bin' if tb else 'b.bin'),('gold.bin','gold.bin')]:
     f=case/name
     if not f.exists():f.symlink_to(d/target)
    lines.append(' '.join(map(str,[B,M,N,K,dtype,ta,tb,case])))
 groups[group]=len(lines);(root/f'{group}.txt').write_text('\n'.join(lines)+'\n');all_lines.extend(lines)
(root/'flat80.txt').write_text('\n'.join(all_lines)+'\n')
(root/'flat_manifest.json').write_text(json.dumps({'groups':groups,'cases':len(all_lines),'golden':'FP64 of actual stored input values ->FP32; 4 storage layouts; both16bit dtypes; negative rows andtails'},indent=2)+'\n')
print(json.dumps({'groups':groups,'cases':len(all_lines)}),flush=True)
