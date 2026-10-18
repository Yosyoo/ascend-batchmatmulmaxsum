from pathlib import Path
import os,json,subprocess
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_v3/c26/load3d_component');rng=np.random.default_rng(26571016)
shapes=[(128,128,256),(16,128,256),(128,16,256),(48,80,240)]
os.environ['COMPONENT_TA']='1'
rows=[]
for m,n,k in shapes:
 for dtype,typ in [(1,np.float16),(2,bfloat16)]:
  for pattern in ['random']:
   d=root/'cases'/f'{m}_{n}_{k}_{dtype}_{pattern}';d.mkdir(parents=True,exist_ok=True)
   if pattern=='exact':a=(rng.integers(-32,33,(m,k))/16).astype(typ);b=(rng.integers(-32,33,(k,n))/16).astype(typ)
   else:a=rng.uniform(-1,1,(m,k)).astype(typ);b=rng.uniform(-1,1,(k,n)).astype(typ)
   a.T.copy().tofile(d/'a.bin');b.tofile(d/'b.bin');start,count=(128,128) if k==256 else (16,128);gold=(a[:,start:start+count].astype(np.float64)@b[start:start+count,:].astype(np.float64)).astype(np.float32)
   r=subprocess.run([str(root/'build/component'),str(m),str(n),str(k),str(dtype),str(start),str(count)],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
   (d/'run.log').write_text(r.stdout+r.stderr)
   if r.returncode:raise RuntimeError((m,n,k,dtype,pattern,r.returncode,r.stdout[-1000:],r.stderr[-1000:]))
   base=np.fromfile(d/'out0.bin',np.float32).reshape(m,n)
   for mode in range(4):
    v=np.fromfile(d/f'out{mode}.bin',np.float32).reshape(m,n)
    delta=np.abs(v-gold);passed=bool(np.all(np.isfinite(v)) and np.all(delta <=1e-4+np.abs(gold)*1e-4))
    row={'shape':[m,n,k],'dtype':dtype,'pattern':pattern,'mode':mode,'start':start,'count':count,'gold_pass':passed,'maxabs':float(delta.max()),'bitwise_baseline':bool(np.array_equal(v.view(np.uint32),base.view(np.uint32)))};rows.append(row);print(json.dumps(row),flush=True)
   if any(not x['gold_pass'] for x in rows[-4:]):
    (root/'transpose_a_results.json').write_text(json.dumps(rows,indent=2)+'\n');raise RuntimeError('Load3D component mismatch')
(root/'transpose_a_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(f'PASS {len(rows)} matrix comparisons',flush=True)
