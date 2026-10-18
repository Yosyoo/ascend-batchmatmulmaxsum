import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import hashlib,json
import numpy as np
from ml_dtypes import bfloat16

rng=np.random.default_rng(1052418)
rows=[];proof=[]
for i,k in enumerate(range(32,129,8)):
    batch=[1,2,8,64][i%4]
    m=1025 if batch==64 else 1024 if batch==8 else 4097 if batch==2 else 8191
    n=[33,40,47,64][(i//4+i)%4]
    assert batch*m*k<=2**26 and batch*n*k<=2**26
    for dtype in [1,2]:
        typ=np.float16 if dtype==1 else bfloat16
        for pattern in ['random','cancel_m','cancel_k']:
            a=rng.uniform(-1,1,(batch,m,k)).astype(typ)
            b=rng.uniform(-1,1,(batch,k,n)).astype(typ)
            if pattern=='cancel_m':
                h=m//2;a[:,h:2*h,:]=-a[:,:h,:];b[:,:,:]=b[:,:,:1]
                if m%2:a[:,-1,:]=0
            if pattern=='cancel_k':
                a[:,:,k//2:]=a[:,:,:k//2];b[:,k//2:,:]=-b[:,:k//2,:]
            gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
            for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
                d=Path('pair_edge_cases')/f'c{len(rows):03d}';d.mkdir(parents=True,exist_ok=True)
                (a.swapaxes(-1,-2).copy() if ta else a).tofile(d/'x1.bin')
                (b.swapaxes(-1,-2).copy() if tb else b).tofile(d/'x2.bin')
                gold.tofile(d/'gold.bin')
                rows.append(' '.join(map(str,(batch,m,n,k,dtype,ta,tb,d.resolve()))))
                proof.append({'case':len(rows)-1,'shape':[batch,m,n,k],'dtype':dtype,'ta':ta,'tb':tb,'pattern':pattern,'sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in d.glob('*.bin')}})
Path('pair_edge_cases.txt').write_text('\n'.join(rows)+'\n')
Path('pair_edge_input_sha256.json').write_text(json.dumps({'seed':1052418,'cases':proof},indent=2)+'\n')
assert len(rows)==312
print('GENERATED',len(rows),'legal paired-path K granularity and batch edge cases',flush=True)
