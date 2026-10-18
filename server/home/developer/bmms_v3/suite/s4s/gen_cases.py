import os, ast
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
shapes=[]
for node in ast.parse(Path('test_suite.py').read_text()).body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='shapes' for t in node.targets): shapes=ast.literal_eval(node.value)
    if isinstance(node,ast.AugAssign) and isinstance(node.target,ast.Name) and node.target.id=='shapes': shapes+=ast.literal_eval(node.value)
rng=np.random.default_rng(1032026);rows=[]
for shape in shapes:
 for dtype in (1,2):
  for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
   B,M,N,K=shape;typ=np.float16 if dtype==1 else bfloat16
   a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if shape in ((2,3,7,40),(1,8,8,32),(1,32,32,32)): a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   golden=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   d=Path('cases')/f'c{len(rows):03d}';d.mkdir(parents=True,exist_ok=True)
   (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin');(b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin');golden.tofile(d/'gold.bin')
   rows.append(' '.join(map(str,(*shape,dtype,ta,tb,str(d.resolve())))))
Path('cases.txt').write_text('\n'.join(rows)+'\n');print('GENERATED',len(rows),'cases')
