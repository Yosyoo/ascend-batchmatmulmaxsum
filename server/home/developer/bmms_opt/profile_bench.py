import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from ml_dtypes import bfloat16
root=Path('/home/developer/bmms_opt')
variants=sys.argv[1:] or ['baseline','candidate']
cases=[(2,3,7,40),(3,17,19,72),(1,65,129,128),(2,129,257,256),(1,31,513,8192),(1,8192,17,32),(1,16,8192,64),(4,256,256,128),(1,512,512,512),(1,1024,1024,1024),(1,256,4096,1024)]
if os.getenv('BENCH_CASES'): cases=[cases[int(i)] for i in os.environ['BENCH_CASES'].split(',')]
results=[]
for shape in cases:
 B,M,N,K=shape
 rng=np.random.default_rng(12345)
 a=rng.uniform(-1,1,(B,M,K)).astype(np.float16); b=rng.uniform(-1,1,(B,K,N)).astype(np.float16)
 golden=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
 for variant in variants:
  tag='_'.join(map(str,shape)); d=root/'bench'/tag/variant; d.mkdir(parents=True,exist_ok=True)
  (d/'input').mkdir(exist_ok=True);(d/'output').mkdir(exist_ok=True)
  a.tofile(d/'input/x1.bin');b.tofile(d/'input/x2.bin')
  command=f'{root/variant}/build/batch_matmul_max_sum_custom {B} {M} {N} {K} 1 0 0 20'
  p=subprocess.run(['msprof','--application='+command,'--output='+str(d/'profile'),'--aic-metrics=PipeUtilization','--task-time=on'],cwd=d,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=150)
  (d/'profile.log').write_text(p.stdout)
  if p.returncode: print(p.stdout,flush=True);raise RuntimeError((shape,variant,p.returncode))
  y=np.fromfile(d/'output/y.bin',np.float32); ok=np.allclose(y,golden,atol=1e-4,rtol=1e-4)
  files=sorted((d/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
  rows=list(csv.DictReader(files[-1].open())); times=[float(r['Task Duration(us)']) for r in rows]
  out={'shape':shape,'variant':variant,'mean_us':float(np.mean(times[2:])),'median_us':float(np.median(times[2:])),'tasks':len(times),'passed':bool(ok),'relative':float(np.max(abs(y-golden)/np.maximum(abs(golden),1e-5)))}
  results.append(out);print(json.dumps(out),flush=True)
  (root/'benchmark_results.json').write_text(json.dumps(results,indent=2))
  if not ok:raise RuntimeError(('precision',y.tolist(),golden.tolist()))
