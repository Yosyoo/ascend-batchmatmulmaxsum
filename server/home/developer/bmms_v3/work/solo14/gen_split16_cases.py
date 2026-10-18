import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052414)
rows = []
for batch in [1]:
    for k in [8176, 8208, 12288, 16384, 16400]:
        if batch == 5 and k != 2048:
            continue
        for dtype in [1, 2]:
            typ = np.float16 if dtype == 1 else bfloat16
            patterns = ['random', 'negative', 'cancel']
            if True:
                patterns.append('cancel_k')
            for pattern in patterns:
                a = rng.uniform(-1, 1, (batch, 64, k)).astype(typ)
                b = rng.uniform(-1, 1, (batch, k, 64)).astype(typ)
                if pattern == 'negative':
                    a = np.abs(a).astype(typ); b = -np.abs(b).astype(typ)
                elif pattern == 'cancel':
                    # Identical N columns and opposite M rows force a near-zero batch sum.
                    a[:, 32:, :] = -a[:, :32, :]
                    b[:, :, :] = b[:, :, :1]
                elif pattern == 'cancel_k':
                    a[:, :, k//2:] = a[:, :, :k//2]
                    b[:, k//2:, :] = -b[:, :k//2, :]
                golden = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                for ta, tb in [(0,0),(0,1),(1,0),(1,1)]:
                    d = Path('split16_cases') / f'c{len(rows):03d}'
                    d.mkdir(parents=True, exist_ok=True)
                    (a.swapaxes(-1,-2).copy() if ta else a).tofile(d / 'x1.bin')
                    (b.swapaxes(-1,-2).copy() if tb else b).tofile(d / 'x2.bin')
                    golden.tofile(d / 'gold.bin')
                    rows.append(' '.join(map(str, (batch,64,64,k,dtype,ta,tb,d.resolve()))))
Path('split16_cases.txt').write_text('\n'.join(rows)+'\n')
print('GENERATED',len(rows),'split and fallback cases')
