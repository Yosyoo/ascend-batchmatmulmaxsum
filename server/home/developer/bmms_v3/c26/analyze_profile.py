import csv,json,statistics
from pathlib import Path
root=Path('/home/developer/bmms_v3')
for v in ['clean10','clean11']:
 files=list((root/'variants'/v/'work/1_1025_1031_1032_2_1_1/profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
 assert files,v
 rows=list(csv.DictReader(files[-1].open())); warm=rows[-60:]
 d={'variant':v,'tasks':len(rows),'warm_count':len(warm),'metrics':{}}
 for k in rows[0]:
  if any(a in k.lower() for a in ['duration','time(us)','ratio','bandwidth','utilization']):
   try:d['metrics'][k]=statistics.median(float(x[k]) for x in warm)
   except (ValueError,TypeError):pass
 (root/'c26'/('metrics_'+v+'.json')).write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps(d))
