import os,sys,json,subprocess,shutil,hashlib,time
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
R=Path(__file__).resolve().parent
vs=os.environ.get('VARIANTS','reference,pipeline').split(',')
for v in vs:
 d=R/v
 for f in ['bench.asc','data_utils.h','CMakeLists.txt']:
  if not (d/f).exists() or (d/f).read_bytes() != (R/f).read_bytes():shutil.copyfile(R/f,d/f)
 with open(d/'build.log','w') as log:
  subprocess.run(['cmake','-S',str(d),'-B',str(d/'build')],stdout=log,stderr=log,check=True)
  subprocess.run(['cmake','--build',str(d/'build'),'-j4'],stdout=log,stderr=log,check=True)
 print('BUILT',v,flush=True)
shapes=[(1,1,1,32),(2,3,7,40),(3,17,19,72),(1,65,129,128),(2,129,257,256),(1,31,513,8192),(1,8192,17,32),(1,16,8192,64),(4,256,256,128),(1,512,512,512),(1,1024,1024,1024),(1,256,4096,1024),(1,8191,33,72),(1,8192,64,8192),(1,8192,129,64),(3,255,4096,64)]
if os.environ.get('SHAPES'):shapes=[tuple(map(int,x.split('_'))) for x in os.environ['SHAPES'].split(',')]
layouts=[(1,0,0)] if not os.environ.get('ALL_LAYOUTS') else [(dt,ta,tb) for dt in (1,2) for ta in (0,1) for tb in (0,1)]
if os.environ.get('LAYOUTS'):layouts=[tuple(map(int,x.split('_'))) for x in os.environ['LAYOUTS'].split(',')]
data=R/'data';(data/'input').mkdir(parents=True,exist_ok=True);(data/'output').mkdir(exist_ok=True)
rows=[]
for shape in shapes:
 B,M,N,K=shape
 for dt,ta,tb in layouts:
  rng=np.random.default_rng(191726)
  typ=np.float16 if dt==1 else bfloat16
  a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
  if M==3:a=np.abs(a);b=-np.abs(b)
  gold=np.zeros(B,np.float64)
  bf=b.astype(np.float64)
  for start in range(0,M,128):gold+=(a[:,start:start+128].astype(np.float64)@bf).max(-1).sum(-1)
  gold=gold.astype(np.float32)
  (a.transpose(0,2,1) if ta else a).copy().tofile(data/'input/x1.bin')
  (b.transpose(0,2,1) if tb else b).copy().tofile(data/'input/x2.bin')
  for v in vs:
   cmd=[str(R/v/'build/bench'),*map(str,shape),str(dt),str(ta),str(tb),'30','5']
   p=subprocess.run(cmd,cwd=data,capture_output=True,text=True,timeout=180)
   row={'shape':shape,'dtype':dt,'ta':ta,'tb':tb,'variant':v,'returncode':p.returncode}
   try:
    row.update(json.loads([l for l in p.stdout.splitlines() if l.startswith('{')][-1]))
    y=np.fromfile(data/'output/y.bin',np.float32)
    row.update(passed=bool(np.allclose(y,gold,rtol=1e-4,atol=1e-4)),relative=float(np.max(np.abs(y-gold)/np.maximum(np.abs(gold),1e-5))))
   except Exception:row['error']=(p.stdout+p.stderr)[-1000:]
   rows.append(row);print(json.dumps(row),flush=True)
   (R/os.environ.get('RESULT','results.json')).write_text(json.dumps(rows,indent=2))
print('DONE',flush=True)
