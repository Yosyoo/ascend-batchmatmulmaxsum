"""Correctness fixtures only. No performance inference from this harness."""
from pathlib import Path
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16

root=Path('/home/developer/bmms_v3/c26/fast_cases')
root.mkdir(exist_ok=True)
standard=[(1,1,1,32),(2,3,7,40),(3,17,19,72),(1,65,129,128),
 (2,129,257,256),(1,31,513,8192),(1,8192,17,32),(1,16,8192,64),
 (2,8,8,64),(3,1,8,8),(2,8,1,56),(1,8191,33,72),(1,511,64,128)]
packed=[(1,1025,1031,1032),(2,777,899,1000),(1,1537,513,776),
 (1,520,512,2040),(1,512,1025,1032)]
chunks=[(1,513,2577,1032),(1,2577,513,1032),(2,512,2049,520)]
negative=[(2,3,7,40),(2,777,899,1000)]
rng=np.random.default_rng(26421016)
all_lines=[];groups={}
for group,shapes in [('standard104',standard),('packed40',packed),('chunks24',chunks)]:
 lines=[]
 for shape in shapes:
  B,M,N,K=shape
  for dtype,typ in [(1,np.float16),(2,bfloat16)]:
   d=root/('_'.join(map(str,shape))+f'_{dtype}');d.mkdir(exist_ok=True)
   a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if shape in negative:a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
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
(root/'all168.txt').write_text('\n'.join(all_lines)+'\n')
(root/'manifest.json').write_text(json.dumps({'groups':groups,'cases':len(all_lines),'golden':'FP64 of actual stored input values ->FP32; 4 storage layouts; both16bit dtypes; negative rows andtails'},indent=2)+'\n')
print(json.dumps({'groups':groups,'cases':len(all_lines)}),flush=True)
