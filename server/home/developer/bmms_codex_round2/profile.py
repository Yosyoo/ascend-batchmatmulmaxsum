import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np
import subprocess,csv,json
R=Path(__file__).resolve().parent
shapes=[(1,4096,17,128),(1,8192,17,32),(1,31,513,8192),(1,1024,1024,1024)]
results=[]
for shape in shapes:
 B,M,N,K=shape;rng=np.random.default_rng(66217)
 a=rng.uniform(-1,1,(B,M,K)).astype(np.float16);b=rng.uniform(-1,1,(B,K,N)).astype(np.float16)
 gold=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
 for v in ['reference','selected']:
  d=R/'profiles'/'_'.join(map(str,shape))/v;(d/'input').mkdir(parents=True,exist_ok=True);(d/'output').mkdir(exist_ok=True)
  a.tofile(d/'input/x1.bin');b.tofile(d/'input/x2.bin')
  cmd=str(R/v/'build/bench')+' '+' '.join(map(str,shape))+' 1 0 0 20 1'
  p=subprocess.run(['msprof','--application='+cmd,'--output='+str(d/'profile'),'--aic-metrics=PipeUtilization','--task-time=on'],cwd=d,capture_output=True,text=True,timeout=180)
  (d/'profile.log').write_text(p.stdout+p.stderr)
  if p.returncode:raise RuntimeError((v,shape,p.stderr[-1000:]))
  y=np.fromfile(d/'output/y.bin',np.float32)
  files=sorted((d/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
  rows=list(csv.DictReader(files[-1].open()));times=[float(x['Task Duration(us)']) for x in rows]
  result=dict(shape=shape,variant=v,median_us=float(np.median(times[3:])),mean_us=float(np.mean(times[3:])),tasks=len(rows),passed=bool(np.allclose(y,gold,atol=1e-4,rtol=1e-4)),csv=str(files[-1]))
  print(json.dumps(result),flush=True);results.append(result)
  (R/'profile_results.json').write_text(json.dumps(results,indent=2))
  assert result['passed'] and len(rows)==23
