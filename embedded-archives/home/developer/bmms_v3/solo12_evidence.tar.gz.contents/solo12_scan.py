import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv,json,statistics,sys,shutil
from pathlib import Path
root=Path('/home/developer/bmms_v3')
sys.path.insert(0,str(root/'harness'))
from measure import run_shape
label=sys.argv[1]
variants=sys.argv[2].split(',')
out=root/'solo12_data'/label
out.mkdir(parents=True,exist_ok=False)
with (out/'results.jsonl').open('w') as f:
 for variant in variants:
  for spec in sys.argv[3:]:
   x=run_shape(variant,spec,'msprof',160,1,0)
   original=root/'variants'/variant/'work'/spec
   saved=out/variant/spec
   shutil.copytree(original,saved)
   files=sorted((saved/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
   assert files, x
   rows=list(csv.DictReader(files[-1].open()))
   rows.sort(key=lambda r:float(r['Task Start Time(us)']))
   assert len(rows)==163, f'{len(rows)} tasks; expected one kernel per call'
   times=[float(r['Task Duration(us)']) for r in rows]
   x['kernels_per_call']=1;x['total_warm_us']=statistics.median(times[-80:]);x['total_us']=times
   x['saved_profile']=str(files[-1])
   x['median_metrics']={}
   for key in rows[0]:
    if key.startswith(('aic_','aiv_','cube_')):
     try:x['median_metrics'][key]=statistics.median(float(r[key]) for r in rows[-80:])
     except ValueError:pass
   f.write(json.dumps(x)+'\n');f.flush()
   print(json.dumps({k:v for k,v in x.items() if k not in ('all_us','total_us','median_metrics')}),flush=True)
   assert x.get('passed') and x.get('returncode')==0,x
