"""Stored-input gold only; operator outputs must be computed by the NPU bench."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from pathlib import Path
import hashlib
import json
import numpy as np
from ml_dtypes import bfloat16

rng = np.random.default_rng(1052419)
rows = []
hashes = {}
for batch in [1, 2, 20, 40, 41, 64]:
    for k in [32, 40, 64]:
        for dtype in [1, 2]:
            typ = np.float16 if dtype == 1 else bfloat16
            for pattern in ['random', 'negative', 'cancel_k', 'zero']:
                a = rng.uniform(-1, 1, (batch, 1, k)).astype(typ)
                b = rng.uniform(-1, 1, (batch, k, 1)).astype(typ)
                if pattern == 'negative':
                    a = np.abs(a).astype(typ)
                    b = -np.abs(b).astype(typ)
                if pattern == 'cancel_k':
                    a[:, :, k // 2:] = a[:, :, :k // 2]
                    b[:, k // 2:, :] = -b[:, :k // 2, :]
                if pattern == 'zero':
                    a[:] = 0
                gold = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
                for ta, tb in [(0, 0), (0, 1), (1, 0), (1, 1)]:
                    directory = Path('dot_once_cases') / ('c%03d' % len(rows))
                    directory.mkdir(parents=True, exist_ok=True)
                    (a.swapaxes(-1, -2).copy() if ta else a).tofile(directory / 'x1.bin')
                    (b.swapaxes(-1, -2).copy() if tb else b).tofile(directory / 'x2.bin')
                    gold.tofile(directory / 'gold.bin')
                    for name in ['x1.bin', 'x2.bin', 'gold.bin']:
                        path = directory / name
                        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
                    rows.append(' '.join(map(str, (batch, 1, 1, k, dtype, ta, tb, directory.resolve()))))
assert len(rows) == 576
Path('dot_once_cases.txt').write_text('\n'.join(rows) + '\n')
Path('dot_once_input_sha256.json').write_text(json.dumps(hashes, indent=2) + '\n')
print('GENERATED', len(rows), 'official-range dot cases; no operator computation performed', flush=True)
