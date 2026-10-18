import json, os, subprocess, time
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
os.environ['OPENBLAS_NUM_THREADS'] = '1'
Path('input').mkdir(exist_ok=True); Path('output').mkdir(exist_ok=True)
rng=np.random.default_rng(1032026)
shapes=[(1,8192,17,256),(4,256,256,128)]
results=[]
for shape in shapes:
 for dtype in (1,2):
  for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
   B,M,N,K=shape
   typ=np.float16 if dtype==1 else bfloat16
   a=rng.uniform(-1,1,(B,M,K)).astype(typ)
   b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if shape==(2,3,7,40): a=np.abs(a).astype(typ); b=-np.abs(b).astype(typ)
   golden=(a.astype(np.float64)@b.astype(np.float64)).max(axis=-1).sum(axis=-1).astype(np.float32)
   (np.swapaxes(a,-1,-2).copy() if ta else a).tofile('input/x1.bin')
   (np.swapaxes(b,-1,-2).copy() if tb else b).tofile('input/x2.bin')
   start=time.monotonic()
   proc=subprocess.run(['./build/batch_matmul_max_sum_custom',*map(str,shape),str(dtype),str(ta),str(tb)],capture_output=True,text=True,timeout=45)
   if proc.returncode: print(proc.stdout,proc.stderr,flush=True); raise RuntimeError((shape,dtype,ta,tb,proc.returncode))
   y=np.fromfile('output/y.bin',np.float32)
   absolute=float(np.max(np.abs(y-golden))) if y.shape==golden.shape else float('inf')
   relative=float(np.max(np.abs(y-golden)/np.maximum(np.abs(golden),1e-5))) if y.shape==golden.shape else float('inf')
   ok=y.shape==golden.shape and np.isfinite(y).all() and np.allclose(y,golden,atol=1e-4,rtol=1e-4)
   result=dict(shape=shape,dtype=dtype,ta=ta,tb=tb,absolute=absolute,relative=relative,passed=bool(ok),seconds=time.monotonic()-start)
   print(json.dumps(result),flush=True); results.append(result)
   if not ok: print('actual',y,'golden',golden,flush=True); raise RuntimeError('precision failure')
Path('test_results.json').write_text(json.dumps(results,indent=2))
print(f'PASS: {len(results)} cases',flush=True)
