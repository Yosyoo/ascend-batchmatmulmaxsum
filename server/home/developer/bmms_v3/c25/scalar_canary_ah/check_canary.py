import os,subprocess,json
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
r=Path('/home/developer/bmms_v3/c25/scalar_canary_ah');w=r/'work';(w/'input').mkdir(parents=True,exist_ok=True);(w/'output').mkdir(exist_ok=True);rng=np.random.default_rng(10532);rows=[]
for b in [1,2,20]:
 for dt,typ in [(1,np.float16),(2,bfloat16)]:
  a=rng.uniform(-1,1,(b,32)).astype(typ);c=rng.uniform(-1,1,(b,32)).astype(typ);a.tofile(w/'input/x1.bin');c.tofile(w/'input/x2.bin');ref=(a.astype(np.float64)*c.astype(np.float64)).sum(-1).astype(np.float32)
  p=subprocess.run([str(r/'build/canary'),str(b),'1','1','32',str(dt),'0','0','1','1'],cwd=w,capture_output=True,text=True,timeout=60,env=dict(os.environ,BMMS_DEVICE_ID='0'))
  y=np.fromfile(w/'output/y.bin',np.float32) if (w/'output/y.bin').exists() else np.empty(0)
  ok=p.returncode==0 and 'CANARY PASS' in p.stdout and y.shape==ref.shape and np.allclose(y,ref,rtol=1e-4,atol=1e-4)
  row={'B':b,'dtype':dt,'passed':bool(ok),'rc':p.returncode,'stdout':p.stdout,'stderr':p.stderr[-500:]};rows.append(row);print(json.dumps(row),flush=True)
(r/'results.json').write_text(json.dumps(rows,indent=2));assert all(x['passed'] for x in rows)
