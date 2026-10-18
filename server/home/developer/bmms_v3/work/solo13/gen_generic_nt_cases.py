import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052313)
rows = []
for m, n in [(3,13),(3,16),(4,9),(4,16),(5,8),(7,13),(8,8),(8,16),
             (2,16),(9,13),(7,17)]:
    for k in [8,16,24,32,40,48,56,64,72]:
        for batch in [20,21,40,41,64]:
            for dtype in [1,2]:
                typ = np.float16 if dtype == 1 else bfloat16
                for pattern in ['random','negative','cancel']:
                    a = rng.uniform(-1,1,(batch,m,k)).astype(typ)
                    b = rng.uniform(-1,1,(batch,k,n)).astype(typ)
                    if pattern == 'negative':
                        a = np.abs(a).astype(typ)
                        b = -np.abs(b).astype(typ)
                    if pattern == 'cancel':
                        h = m//2
                        a[:,h:2*h,:] = -a[:,:h,:]
                        if m % 2:
                            a[:,-1,:] = 0
                        b[:,:,:] = b[:,:,:1]
                    gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                    d = Path('generic_nt_cases') / f'c{len(rows):04d}'
                    d.mkdir(parents=True, exist_ok=True)
                    a.tofile(d/'x1.bin')
                    b.swapaxes(-1,-2).copy().tofile(d/'x2.bin')
                    gold.tofile(d/'gold.bin')
                    rows.append(' '.join(map(str,(batch,m,n,k,dtype,0,1,d.resolve()))))
Path('generic_nt_cases.txt').write_text('\n'.join(rows)+'\n')
assert len(rows) == 2970
print('GENERATED', len(rows), 'generic NT and dispatch boundary cases', flush=True)
