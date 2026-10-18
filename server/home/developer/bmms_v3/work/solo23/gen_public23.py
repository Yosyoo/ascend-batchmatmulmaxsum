from pathlib import Path
import hashlib,json,numpy as np
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';p=d/'public_case1_23';p.mkdir(exist_ok=False)
# Exactly the public generator's RandomState(42), uniform[-1,1], stored FP16 inputs.
rng=np.random.RandomState(42)
a=rng.uniform(-1.,1.,(1,1,32)).astype(np.float16);b=rng.uniform(-1.,1.,(1,32,1)).astype(np.float16)
gold=np.matmul(a.astype(np.float64),b.astype(np.float64)).max(axis=1).sum(axis=1).astype(np.float32)
a.tofile(p/'x1.bin');b.tofile(p/'x2.bin');gold.tofile(p/'gold.bin')
(d/'public_case1_23.txt').write_text(f'1 1 1 32 1 0 0 {p}\n')
meta=dict(shape=[1,1,1,32],dtype=1,ta=0,tb=0,seed=42,gold=gold.tolist(),reference='CPU FP64 matmul thenFP32; inputs match official public generator',
    files={f.name:dict(bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in p.iterdir() if f.is_file()})
(p/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
