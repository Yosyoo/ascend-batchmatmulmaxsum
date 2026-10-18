import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv,json,statistics,sys
from pathlib import Path
root=Path('/home/developer/bmms_v3')
sys.path.insert(0,str(root/'harness'))
from measure import run_shape
variants=sys.argv[1].split(',')
out=root/'solo8_data'/(os.environ.get('BMMS_SCAN_LABEL','scan')+'_'+'_'.join(variants)+'.jsonl')
with out.open('w') as f:
 for variant in variants:
  for spec in sys.argv[2:]:
   x=run_shape(variant,spec,'msprof',160,1,0)
   path=root/'variants'/variant/'work'/spec/'profile'
   files=sorted(path.glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
   if not files:
    print(json.dumps(x),flush=True);raise SystemExit(1)
   rows=list(csv.DictReader(files[-1].open()))
   rows.sort(key=lambda r:float(r['Task Start Time(us)']))
   assert len(rows)%163==0
   count=len(rows)//163
   assert count in (1,2)
   total=[sum(float(r['Task Duration(us)']) for r in rows[i:i+count]) for i in range(0,len(rows),count)]
   x['kernels_per_call']=count;x['total_warm_us']=statistics.median(total[-80:]);x['total_us']=total
   x['stage_warm_us']={name:statistics.median([float(r['Task Duration(us)']) for r in rows if r['Op Name']==name][-80:]) for name in sorted(set(r['Op Name'] for r in rows))}
   f.write(json.dumps(x)+'\n');f.flush()
   print(json.dumps({k:v for k,v in x.items() if k not in ('all_us','total_us')}),flush=True)
   if not x.get('passed'):raise SystemExit(2)
