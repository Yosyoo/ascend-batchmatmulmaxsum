import os, subprocess, sys
os.environ["OPENBLAS_NUM_THREADS"]="1"
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
variants=sys.argv[1].split(",")
shapes=[tuple(int(x) for x in s.split("_")) for s in sys.argv[2].split(",")]
rng=np.random.default_rng(1032026)
for shape in shapes:
  for dtype in (1,2):
    for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
      B,M,N,K=shape
      typ=np.float16 if dtype==1 else bfloat16
      a=rng.uniform(-1,1,(B,M,K)).astype(typ); b=rng.uniform(-1,1,(B,K,N)).astype(typ)
      if shape==(2,3,7,40): a=np.abs(a).astype(typ); b=-np.abs(b).astype(typ)
      golden=(a.astype(np.float64)@b.astype(np.float64)).max(axis=-1).sum(axis=-1).astype(np.float32)
      parts=[]
      for v in variants:
        d=Path("/home/developer/bmms_opt")/v
        (np.swapaxes(a,-1,-2).copy() if ta else a).tofile(d/"input"/"x1.bin")
        (np.swapaxes(b,-1,-2).copy() if tb else b).tofile(d/"input"/"x2.bin")
        p=subprocess.run(["./build/batch_matmul_max_sum_custom",*map(str,shape),str(dtype),str(ta),str(tb)],cwd=d,capture_output=True,text=True,timeout=120)
        if p.returncode:
          parts.append(v+":RC="+str(p.returncode)); continue
        y=np.fromfile(d/"output"/"y.bin",np.float32)
        ok=(y.shape==golden.shape) and bool(np.allclose(y,golden,atol=1e-4,rtol=1e-4))
        tag="OK" if ok else "BAD "+str(y.tolist())
        parts.append(v+":"+tag)
      print(str(shape)+" dt="+str(dtype)+" ta="+str(ta)+" tb="+str(tb)+"  golden="+str(golden.tolist())+"  "+"  ".join(parts),flush=True)
