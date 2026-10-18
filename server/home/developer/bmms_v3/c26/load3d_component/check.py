from pathlib import Path
import os,json,subprocess
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/load3d_component');rng=np.random.default_rng(26571016)
shapes=[(16,16,32),(32,64,64),(64,32,128),(128,128,128),(48,80,240),(128,64,256),(16,128,256),(128,16,32)]
rows=[]
for m,n,k in shapes:
 for dtype,typ in [(1,np.float16),(2,bfloat16)]:
  for pattern in ['exact','random']:
   d=root/'cases'/f'{m}_{n}_{k}_{dtype}_{pattern}';d.mkdir(parents=True,exist_ok=True)
   if pattern=='exact':a=(rng.integers(-32,33,(m,k))/16).astype(typ);b=(rng.integers(-32,33,(k,n))/16).astype(typ)
   else:a=rng.uniform(-1,1,(m,k)).astype(typ);b=rng.uniform(-1,1,(k,n)).astype(typ)
   a.tofile(d/'a.bin');b.tofile(d/'b.bin');gold=(a.astype(np.float64)@b.astype(np.float64)).astype(np.float32)
   r=subprocess.run([str(root/'build/component'),str(m),str(n),str(k),str(dtype)],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
   (d/'run.log').write_text(r.stdout+r.stderr)
   if r.returncode:raise RuntimeError((m,n,k,dtype,pattern,r.returncode,r.stdout[-1000:],r.stderr[-1000:]))
   base=np.fromfile(d/'out0.bin',np.float32).reshape(m,n)
   for mode in range(4):
    v=np.fromfile(d/f'out{mode}.bin',np.float32).reshape(m,n)
    delta=np.abs(v-gold);passed=bool(np.all(np.isfinite(v)) and np.all(delta <=1e-4+np.abs(gold)*1e-4))
    row={'shape':[m,n,k],'dtype':dtype,'pattern':pattern,'mode':mode,'gold_pass':passed,'maxabs':float(delta.max()),'bitwise_baseline':bool(np.array_equal(v.view(np.uint32),base.view(np.uint32)))};rows.append(row);print(json.dumps(row),flush=True)
   if any(not x['gold_pass'] for x in rows[-4:]):
    (root/'results.json').write_text(json.dumps(rows,indent=2)+'\n');raise RuntimeError('Load3D component mismatch')
(root/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(f'PASS {len(rows)} matrix comparisons',flush=True)
