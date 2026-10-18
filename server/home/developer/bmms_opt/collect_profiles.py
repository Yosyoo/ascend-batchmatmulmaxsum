import csv,json,shutil
from pathlib import Path
root=Path('/home/developer/bmms_opt')
out=root/'collected_profiles';out.mkdir(exist_ok=True)
metrics={}
for variant in ['baseline','final','balanced']:
 for d in sorted((root/'bench').glob('*/'+variant)):
  files=sorted((d/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
  if not files:continue
  f=files[-1];tag=d.parent.name
  shutil.copy2(f,out/(variant+'_'+tag+'.csv'))
  rows=list(csv.DictReader(f.open()))
  if tag=='4_256_256_128':
   vals={}
   for key in rows[0]:
    try: vals[key]=sum(float(row[key]) for row in rows[2:])/len(rows[2:])
    except(ValueError,TypeError):pass
   metrics[variant]=vals
(out/'profile_summary.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({v:{k:n for k,n in x.items() if k=='Task Duration(us)' or 'ratio' in k or 'utilization' in k} for v,x in metrics.items()},indent=2))
